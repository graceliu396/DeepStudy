from semantic_kernel.functions import kernel_function
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.core.config import settings
from typing import Annotated
import requests

class Dalle3Plugin:
    @kernel_function(description="Provide a vivid image based on the description")
    def generate_image_with_dalle3(
        self, input_prompt: Annotated[str, "The prompt used to generate the image"]
    ) -> Annotated[str, "Returns the url of the image"]:
        endpoint = settings.AZURE_AI_ENDPOINT_DALLE
        deployment_name = settings.AZURE_AI_DALLE_NAME
        api_version = "2024-02-01"
        api_key = settings.AZURE_AI_KEY_DALLE
        
        url = f"{endpoint}/openai/deployments/{deployment_name}/images/generations?api-version={api_version}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        
        payload ={
            "model": "dall-e-3",
            "prompt": input_prompt,
            "size": "1024x1024",
            "style": "vivid",
            "quality": "standard",
            "n": 1
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result['data'][0]['url']
        

if __name__ == "__main__":
    plugin=Dalle3Plugin()
    result = plugin.generate_image_with_dalle3("A photograph of a red fox in an autumn forest")
    print(result)