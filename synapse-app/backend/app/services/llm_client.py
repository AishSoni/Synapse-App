"""
LiteLLM Client for Claude Sonnet 4 and Gemini Embeddings
Uses custom proxy endpoint
"""

import os
import httpx
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
import base64

load_dotenv()

class LiteLLMClient:
    """Client for LiteLLM proxy supporting multiple models"""

    def __init__(self):
        # Load from root .env
        root_env_path = os.path.join(os.path.dirname(__file__), '../../../.env')
        load_dotenv(root_env_path)

        self.base_url = os.getenv("BASE_URL")
        self.auth_token = os.getenv("AUTH_TOKEN")

        if not self.base_url or not self.auth_token:
            raise ValueError("BASE_URL and AUTH_TOKEN must be set in .env")

        print(f"[OK] LiteLLM proxy configured: {self.base_url}")

        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Call LLM for chat completion

        Args:
            messages: List of {role, content} messages
            model: Model name (default: claude-sonnet-4-5-20250929)
            temperature: Sampling temperature
            max_tokens: Max response tokens

        Returns:
            Response text
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )

                if response.status_code != 200:
                    error_detail = response.text
                    print(f"LiteLLM API Error {response.status_code}: {error_detail}")
                    raise Exception(f"LiteLLM API returned {response.status_code}: {error_detail}")

                response.raise_for_status()
                data = response.json()

                return data["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"Error in chat completion: {e}")
            raise

    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str,
        model: str = "claude-sonnet-4-5-20250929"
    ) -> str:
        """
        Analyze image using vision model

        Args:
            image_data: Image bytes
            prompt: Analysis prompt
            model: Vision-capable model

        Returns:
            Analysis result
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Use OpenAI-compatible vision format for LiteLLM
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": 1000
                    }
                )

                response.raise_for_status()
                data = response.json()

                return data["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"Error analyzing image: {e}")
            raise

    async def create_embedding(
        self,
        text: str,
        model: str = "gemini-embedding-001"
    ) -> List[float]:
        """
        Generate embedding vector

        Args:
            text: Text to embed
            model: Embedding model (default: gemini-embedding-001)

        Returns:
            Embedding vector (list of floats)
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=self.headers,
                    json={
                        "model": model,
                        "input": text
                    }
                )

                response.raise_for_status()
                data = response.json()

                return data["data"][0]["embedding"]

        except Exception as e:
            print(f"Error creating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 768

# Singleton instance
_llm_client = None

def get_llm_client() -> LiteLLMClient:
    """Get or create LiteLLM client singleton"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LiteLLMClient()
    return _llm_client
