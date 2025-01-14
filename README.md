# AWS RAG Chatbot

This code creates a RAG based chatbot using AWS AI based services, namely Amazon Bedrock where we use its Knowledge Bases and Agent features and deploys it in a Streamlit application. It further uses AWS's S3 and IAM services for other requirements. 
This project builds on the RAG based chatbot solution provided by https://www.youtube.com/watch?v=VGL6_k1DuDE [ Aniket Wattamwar ] by adding ingestion features so as to automatically sync the data at the Data Source
This chatbot answers any question using the knowledge base provided and further gives you the option to add your own knowledge base which automatically ingests (syncs) the Data Source on which you can now ask questions based on the original knowledge base on your newly ingested document.

Below are the results obtained: 

Below shows the Landing page of the streamlit application that contains a chatbot to chat with the bot/model. And another button to add your own document/knowledge to the existing knowledge base.
![Landing Page](images/Landing.png)

I had initially added 4 documents about Mars travel in my S3 bucket for the knowledge base and it provided pretty good results.
![Chat 1](images/chat_1.png)

Now to add your own documents this how it looks.
![KB1](images/Add_Knowledge.png)
![KB2](images/Add_Knowledge_2.png)

I added a document containing information about myself and this is how it responded after the ingestion process.
![Chat 2](images/chat_2.png)

---
### Architecture Diagram


---

### Execution Steps

1) Create an IAM User and provide the following Permissions policies to your user
