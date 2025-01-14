import itertools  # For advanced iteration
import boto3  # AWS SDK for Python
import chromadb  # For handling vectorized databases (if applicable)
from botocore.exceptions import ClientError  # For handling AWS client errors
from oauthlib.uri_validate import query  # For validating URIs
from dotenv import load_dotenv  # For loading environment variables from a .env file
import os  # For accessing environment variables

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
# Constants
# -------------------------------
MAX_MESSAGES = 10  # Maximum number of messages to retain in the chat history

# -------------------------------
# ChatMessage Class
# -------------------------------
class ChatMessage:
    """
    Represents a chat message, including its role (user/assistant) and text content.
    """
    def __init__(self, role, text):
        """
        Initialize a ChatMessage object.
        
        Args:
            role (str): Role of the message sender ('user' or 'assistant').
            text (str): Text content of the message.
        """
        self.role = role
        self.text = text


# -------------------------------
# Chat with Model Functionality
# -------------------------------
def chat_with_model(message_history, new_text=None):
    """
    Interacts with the Bedrock Foundation Model to generate responses based on the knowledge base.

    Args:
        message_history (list): List of ChatMessage objects representing the conversation history.
        new_text (str): New user message to be added to the conversation.

    Returns:
        None
    """
    # Initialize a Boto3 session
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id_tarun,
        aws_secret_access_key=aws_secret_access_key_tarun,
        region_name=region_name_tarun
    )

    # Bedrock runtime client for interacting with the foundation model
    bedrock_agent_runtime_client = session.client("bedrock-agent-runtime", region_name='us-east-1')

    # Amazon Titan foundation model ARN
    model_arn = f'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-premier-v1:0'

    # Add the new user message to the message history
    new_text_message = ChatMessage('user', text=new_text)
    message_history.append(new_text_message)

    # Ensure the number of stored messages does not exceed the maximum allowed
    number_of_messages = len(message_history)
    if number_of_messages > MAX_MESSAGES:
        del message_history[
            0: (number_of_messages - MAX_MESSAGES) * 2
        ]  # Remove both user and assistant messages if history exceeds the limit

    # Call Bedrock's retrieve_and_generate API to generate a response
    response = bedrock_agent_runtime_client.retrieve_and_generate(
        input={
            'text': new_text
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': knowledge_base_id_tarun,
                'modelArn': model_arn
            }
        },
    )

    # Extract the generated text from the API response
    generated_text = response['output']['text']

    # Add the assistant's response to the message history
    response_chat_message = ChatMessage('assistant', generated_text)
    message_history.append(response_chat_message)

    # (Optional) Retrieve specific knowledge using the retrieve API
    retrieval_response = bedrock_agent_runtime_client.retrieve(
        knowledgeBaseId=knowledge_base_id_tarun,
        retrievalQuery={
            'text': new_text
        }
    )
    print(retrieval_response)

    return
