from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
import numpy as np

endpoint = "https://edupdfparser.cognitiveservices.azure.com/"
key = "2cJ9tsf0Qj2mEt2l3CtkPYNYk1ma8xfZUgwJjiMnIkeSCeEXADspJQQJ99BDACYeBjFXJ3w3AAALACOGkr3h"


document_intelligence_client = DocumentIntelligenceClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

def analyze_pdf(file_content: bytes):
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-read", file_content, content_type="application/pdf"
    )
    result = poller.result()
    return result.content

