import sys
import uuid
from pathlib import Path
print(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

import logging
import os
from datetime import datetime
from typing import List, Dict
import re

from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential
from app.schemas.uploadFile import *
from app.core.config import settings
logging.basicConfig(level=logging.ERROR)


cosmos_client = None
database = None
container = None

# Define Cosmos DB containers
file_container = None
chat_history_container = None

try:
    credential = DefaultAzureCredential()
    cosmos_client=CosmosClient.from_connection_string(settings.AZURE_COSMOS_DB_CONNECTION_STRING)
    print("[DEBUG] Connected to Cosmos DB successfully using DefaultAzureCredential.")
except Exception as dac_error:
    print(f"[ERROR] Failed to authenticate using DefaultAzureCredential: {dac_error}")
    raise dac_error

# Initialize Cosmos DB client and containers
try:
    database = cosmos_client.get_database_client(settings.AZURE_COSMOS_DB_DATABASE_NAME)
    print(f"[DEBUG] Connected to Cosmos DB: {settings.AZURE_COSMOS_DB_DATABASE_NAME}")


    file_container = database.get_container_client("uploadFile")
    chat_history_container = database.get_container_client("chatHistory")

except Exception as e:
    print(f"[ERROR] Error initializing Cosmos DB Containers: {e}")
    raise e


# TODO 在CCSS中，根据用户上传的文件内容，进行向量搜索，返回相似的文件
# def vector_search(vectors, adminId, subject, grade, topic):


def update_file_container(data):
    try:
        file_container.upsert_item(data)
        logging.debug(f"User data saved to Cosmos DB: {data}")
    except Exception as e:
        print(f"[ERROR] Error saving user data to Cosmos DB: {e}")
        raise e



def update_chat_history_container(data):
    try:
        chat_history_container.upsert_item(data)
        print(f"[DEBUG] Chat history data saved to Cosmos DB: {data}")
    except Exception as e:
        print(f"[ERROR] Error saving Chat history data to Cosmos DB: {e}")
        raise e


def fetch_file_by_id(fileId):
    try:
        query = f"SELECT * FROM c WHERE c.id = '{fileId}'"
        items = list(file_container.query_items(query=query, enable_cross_partition_query=True))
        print(f"[DEBUG] Fetched {len(items)} file data for fileId: {fileId}")
        return items
    except Exception as e:
        print(f"[ERROR] Error fetching file data for fileId: {fileId}: {e}")
        raise e


def fetch_file_by_user_id(userId):
    try:
        query = f"SELECT * FROM c WHERE c.user_id = '{userId}'"
        items = list(file_container.query_items(query=query, enable_cross_partition_query=True))
        print(f"[DEBUG] Fetched {len(items)} file data for userId: {userId}")
        return items
    except Exception as e:
        print(f"[ERROR] Error fetching file data for userId: {userId}: {e}")
        raise e

    
def fetch_chat_history_by_user_file_session_id(userId, fileId, sessionId):
    try:
        query = f"SELECT * FROM c WHERE c.user_id = '{userId}' AND c.file_id = '{fileId}' AND c.session_id = '{sessionId}'"
        items = list(chat_history_container.query_items(query=query, enable_cross_partition_query=True))
        print(f"[DEBUG] Fetched {len(items)} chat history data for userId: {userId}, fileId: {fileId}, sessionId: {sessionId}")
        return items
    except Exception as e:
        print(f"[ERROR] Error fetching chat history data for userId: {userId}, fileId: {fileId}, sessionId: {sessionId}: {e}")
        raise e



def patch_lesson_plan(fileId, userId, lesson_plan):
    try:
        print("fileId: ", fileId)
        print("userId: ", userId)
        print("lesson_plan: ", lesson_plan)

        operations = [{'op': 'replace', 'path': '/lesson_plan', 'value': lesson_plan}]
        partition_key = [userId]
        file_container.patch_item(item=fileId, partition_key=partition_key, patch_operations=operations)

    except Exception as e:
        print(f"[ERROR] Error patching lesson plan: {e}")
        raise e


def delete_upload_file(fileId):
    try:
        query = f"SELECT * FROM c WHERE c.id = '{fileId}'"
        items = list(file_container.query_items(query=query, enable_cross_partition_query=True))
        if len(items) == 0:
            print(f"[DEBUG] No file data found for fileId: {fileId}")
            return
        for item in items:
            file_container.delete_item(item)
            print(f"[DEBUG] Deleted file data for fileId: {fileId}")
    except Exception as e:
        print(
            f"[ERROR] Error deleting file data for fileId: {fileId}: {e}")
        raise e
    

def delete_chat_history(userId, fileId, sessionId):
    try:
        query = f"SELECT * FROM c WHERE c.user_id = '{userId}' AND c.file_id = '{fileId}' AND c.session_id = '{sessionId}'"
        items = list(chat_history_container.query_items(query=query, enable_cross_partition_query=True))
        if len(items) == 0:
            print(f"[DEBUG] No chat history data found for userId: {userId}, fileId: {fileId}, sessionId: {sessionId}")
            return
        for item in items:
            chat_history_container.delete_item(item, partition_key=[userId, fileId, sessionId])
            print(f"[DEBUG] Deleted chat history data for userId: {userId}, fileId: {fileId}, sessionId: {sessionId}")
    except Exception as e:
        print(f"[ERROR] Error deleting chat history data for userId: {userId}, fileId: {fileId}, sessionId: {sessionId}: {e}")
        raise e

def create_file_record(uploadFile_data):
    print(type(file_container))
    print(type(uploadFile_data))
    try:
        file_container.upsert_item(uploadFile_data)
        print(f"[DEBUG] File record created: {uploadFile_data}")
    except Exception as e:
        print(f"[ERROR] Error creating file record: {e}")
        raise e



def store_chat_history(data):
    try:
        chat_history_container.upsert_item(data)
        print(f"[DEBUG] Chat history saved to Cosmos DB: {data}")
    except Exception as e:
        print(f"[ERROR] Error saving chat history to Cosmos DB: {e}")
        raise e

if __name__ == "__main__":
    print("=================TEST=================")
    with open("D:\Programming\AIAgent\SemanticKernel\plan_data.json", "r", encoding="utf-8") as file:
        plan = Plan.model_validate_json(file.read())
    file_record = FileUpload(
        id=str(uuid.uuid4()),
        user_id="3",
        subject="Math",
        file_topic="Math",
        grade="3",
        file_content="HAHAHAHAHHAHAHAHAHAHAH",
        lesson_plan=plan
    )
    create_file_record(file_record.model_dump())
