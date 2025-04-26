from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
import numpy as np
from app.core.config import settings

endpoint = settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
key = settings.AZURE_DOCUMENT_INTELLIGENCE_KEY


document_intelligence_client = DocumentIntelligenceClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

def analyze_pdf(file_content: bytes):
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-read", file_content, content_type="application/pdf"
    )
    result = poller.result()
    return result.content

