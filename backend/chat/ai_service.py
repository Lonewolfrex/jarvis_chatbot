import os
import requests


class OllamaService:

    MODEL = "llama3.1:8b"

    @staticmethod
    def generate_response(prompt):

        base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://host.docker.internal:11434"
        )

        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": OllamaService.MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()["response"]