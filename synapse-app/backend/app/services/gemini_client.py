import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def get_gemini_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using Gemini
    """
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return zero vector as fallback
        return [0.0] * 768

async def extract_content_with_gemini(html: str, title: str, url: str) -> str:
    """
    Use Gemini to extract and summarize main content from HTML
    """
    try:
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        Extract the main content from this webpage.

        Title: {title}
        URL: {url}

        HTML (truncated):
        {html[:5000]}

        Please provide:
        1. A concise summary of the main content (2-3 sentences)
        2. Key topics or categories
        3. Any important entities (products, people, places, etc.)

        Keep the response structured and concise.
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error extracting content: {e}")
        # Fallback to simple text extraction
        return f"{title}\n\nURL: {url}"
