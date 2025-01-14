# AWS_RAG_Chatbot

This code creates a RAG based chatbot using AWS AI based services, namely Amazon Bedrock where we use its Knowledge Bases and Agent features. It further uses AWS's S3 and IAM services for other requirements.
This chatbot answers any question using the knowledge base provided and further gives you the option to add your own knowledge base which automatically ingests (syncs) the Data Source on which you can now ask questions based on the original knowledge base on your newly ingested document.

Below are the results obtained: 

![Landing Page](images/Landing.pmg)


I had initially added 4 documents about Mars travel in my S3 bucket


---

### Execution Steps

1) Create an IAM User and provide the following Permissions policies to your user
