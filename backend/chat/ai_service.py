import os
import requests
import json

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

    @staticmethod
    def generate_title(message):

        prompt = f"""
            Create a short chat title.

            Rules:
            - max 6 words
            - no punctuation
            - no quotes

            Message:
            {message}
            """

        return OllamaService.generate_response(prompt)

    @staticmethod
    def generate_stream(prompt):

        base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://host.docker.internal:11434"
        )

        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": OllamaService.MODEL,
                "prompt": prompt,
                "stream": True
            },
            stream=True,
            timeout=300
        )

        response.raise_for_status()

        for line in response.iter_lines():

            if not line:
                continue

            try:

                data = json.loads(
                    line.decode("utf-8")
                )

                if "response" in data:
                    yield data["response"]

            except Exception:
                continue

    @staticmethod
    def generate_chat(messages):

        base_url=os.getenv(
            "OLLAMA_BASE_URL",
            "http://host.docker.internal:11434"
        )

        response=requests.post(
            f"{base_url}/api/chat",
            json={
                "model":OllamaService.MODEL,
                "messages":messages,
                "stream":False
            },
            timeout=300
        )

        response.raise_for_status()

        return response.json()["message"]["content"]

    @staticmethod
    def generate_chat_stream(messages):

        base_url=os.getenv(
            "OLLAMA_BASE_URL",
            "http://host.docker.internal:11434"
        )

        response=requests.post(
            f"{base_url}/api/chat",
            json={
                "model":OllamaService.MODEL,
                "messages":messages,
                "stream":True
            },
            stream=True
        )

        response.raise_for_status()

        for line in response.iter_lines():

            if not line:
                continue

            import json

            chunk=json.loads(line)

            if "message" in chunk:

                yield chunk["message"].get(
                    "content",
                    ""
                )

