import time  # Import for polling and delays
import streamlit as st  # Streamlit for building the web interface
import boto3  # AWS SDK for Python
from botocore.exceptions import ClientError  # For handling AWS client errors
from dotenv import load_dotenv  # For loading environment variables from a .env file
import os  # For accessing environment variables
import rag_chatbot_lib as glib  # Reference to the custom chatbot library

# Execution: Run the app using the command `streamlit run rag_chatbot_app.py`

# -------------------------------
# Page Configuration
# -------------------------------
# Set up the Streamlit page configuration (title, layout, etc.)
st.set_page_config(page_title="RAG Chatbot")

# -------------------------------
# Load Environment Variables
# -------------------------------
# Load AWS credentials and configurations from the .env file
load_dotenv()

aws_access_key_id_tarun = os.getenv('aws_access_key_id_tarun')
aws_secret_access_key_tarun = os.getenv('aws_secret_access_key_tarun')
region_name_tarun = os.getenv('region_name_tarun')
bucket_name_tarun = os.getenv('bucket_name_tarun')
knowledge_base_id_tarun = os.getenv('knowledge_base_id_tarun')
data_source_id_tarun = os.getenv('data_source_id_tarun')

# -------------------------------
# Application Title
# -------------------------------
st.title("RAG Chatbot with Amazon Bedrock")

# -------------------------------
# Function Definitions
# -------------------------------

# Upload file to S3
def upload_to_s3(file, bucket_name, object_name=None):
    """
    Uploads a file to an S3 bucket.

    Args:
        file: File object to upload.
        bucket_name: Name of the S3 bucket.
        object_name: Name of the object in the bucket (default: file name).
    """
    if object_name is None:
        object_name = file.name

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id_tarun,
        aws_secret_access_key=aws_secret_access_key_tarun,
        region_name=region_name_tarun
    )
    s3_client = session.client('s3')
    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
        st.success(f"File {file.name} uploaded to S3 bucket {bucket_name} successfully.")
    except ClientError as e:
        st.error(f"ClientError: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Start ingestion job
def start_ingestion_job(knowledge_base_id, data_source_id):
    """
    Starts an ingestion job to sync data with the Knowledge Base.

    Args:
        knowledge_base_id: ID of the Knowledge Base.
        data_source_id: ID of the data source to sync.

    Returns:
        ingestion_job_id: ID of the started ingestion job (if successful).
    """
    try:
        client = boto3.client(
            'bedrock-agent',
            aws_access_key_id=aws_access_key_id_tarun,
            aws_secret_access_key=aws_secret_access_key_tarun,
            region_name=region_name_tarun
        )
        response = client.start_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id
        )
        ingestion_job_id = response['ingestionJob']['ingestionJobId']
        st.success(f"Ingestion job started successfully with ID: {ingestion_job_id}")
        return ingestion_job_id
    except ClientError as e:
        st.error(f"Error starting ingestion job: {e}")
        return None

# Get ingestion job status
def get_ingestion_job_status(knowledge_base_id, data_source_id, ingestion_job_id):
    """
    Retrieves the status of an ingestion job.

    Args:
        knowledge_base_id: ID of the Knowledge Base.
        data_source_id: ID of the data source.
        ingestion_job_id: ID of the ingestion job.

    Returns:
        status: Status of the ingestion job.
    """
    try:
        client = boto3.client(
            'bedrock-agent',
            aws_access_key_id=aws_access_key_id_tarun,
            aws_secret_access_key=aws_secret_access_key_tarun,
            region_name=region_name_tarun
        )
        response = client.get_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id,
            ingestionJobId=ingestion_job_id
        )
        return response['ingestionJob']['status']
    except ClientError as e:
        st.error(f"Error retrieving ingestion job status: {e}")
        return None

# Polling for ingestion job completion
def wait_for_ingestion_completion(knowledge_base_id, data_source_id, ingestion_job_id, timeout=300, poll_interval=10):
    """
    Polls the status of an ingestion job until completion, failure, or timeout.

    Args:
        knowledge_base_id: ID of the Knowledge Base.
        data_source_id: ID of the data source.
        ingestion_job_id: ID of the ingestion job.
        timeout: Maximum time to wait (in seconds).
        poll_interval: Time interval between status checks (in seconds).

    Returns:
        status: Final status of the ingestion job.
    """
    elapsed_time = 0
    while elapsed_time < timeout:
        status = get_ingestion_job_status(knowledge_base_id, data_source_id, ingestion_job_id)
        if status == "COMPLETE":
            st.success("Ingestion job completed successfully!")
            return status
        elif status == "FAILED":
            st.error("Ingestion job failed.")
            return status
        else:
            st.info(f"Ingestion job status: {status}. Waiting...")
            time.sleep(poll_interval)
            elapsed_time += poll_interval

    st.warning("Ingestion job timed out.")
    return "TIMED_OUT"

# -------------------------------
# File Upload and Ingestion
# -------------------------------

# File uploader widget
uploaded_file = st.file_uploader("Upload a file")

# Add Knowledge Button
if st.button("Add Knowledge"):
    if uploaded_file is not None:
        # Step 1: Upload file to S3
        upload_to_s3(uploaded_file, bucket_name_tarun)
        st.success("File uploaded. Starting ingestion...")

        # Step 2: Start ingestion job
        ingestion_job_id = start_ingestion_job(knowledge_base_id_tarun, data_source_id_tarun)
        if ingestion_job_id:
            # Step 3: Wait for ingestion job completion
            st.info("Waiting for ingestion job to complete. This may take a few seconds...")
            final_status = wait_for_ingestion_completion(knowledge_base_id_tarun, data_source_id_tarun, ingestion_job_id)
            if final_status == "COMPLETE":
                st.success("Ingestion job completed successfully!")
            elif final_status == "FAILED":
                st.error("Ingestion job failed.")
    else:
        st.warning("Please upload a file first.")

# -------------------------------
# Chat Interface
# -------------------------------

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Container for chat messages
chat_container = st.container()
input_text = st.chat_input("Chat with your bot here")

# Process chat input
if input_text:
    glib.chat_with_model(message_history=st.session_state.chat_history, new_text=input_text)

# Render chat history
for message in st.session_state.chat_history:
    with chat_container.chat_message(message.role):
        st.markdown(message.text)
