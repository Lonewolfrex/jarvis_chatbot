import requests
import os


class OllamaService:

    MODEL = "llama3.1:8b"

    @staticmethod
    def generate_response(prompt: str):

        base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://172.17.0.1:11434"
        )

        url = f"{base_url}/api/generate"

        payload = {
            "model": OllamaService.MODEL,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(url, json=payload, timeout=60)

            if response.status_code != 200:
                return f"AI service error: {response.text}"

            return response.json().get("response", "")

        except requests.exceptions.RequestException as e:
            return f"AI connection failed: {str(e)}"