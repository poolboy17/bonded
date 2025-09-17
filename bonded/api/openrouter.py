"""
OpenRouter API Client for generating content outlines
"""

import os
from typing import Dict, Any
import aiohttp
import asyncio


class OpenRouterClient:
    """Client for OpenRouter API to generate content outlines using free models"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.session
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def generate_outline(self, row: Dict[str, Any]) -> str:
        """
        Generate a content outline using OpenRouter free model
        
        Args:
            row: CSV row with title and metadata
            
        Returns:
            Generated outline as string
        """
        title = row.get('title', '')
        description = row.get('description', '')
        keywords = row.get('keywords', '')
        target_audience = row.get('target_audience', '')
        
        prompt = self._build_outline_prompt(title, description, keywords, target_audience)
        
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",  # Free model
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert content strategist specializing in creating detailed, SEO-optimized content outlines."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        session = await self._get_session()
        
        try:
            async with session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error {response.status}: {error_text}")
                
                data = await response.json()
                
                if 'choices' not in data or not data['choices']:
                    raise Exception("No response from OpenRouter API")
                
                return data['choices'][0]['message']['content'].strip()
        
        except aiohttp.ClientError as e:
            raise Exception(f"Network error calling OpenRouter API: {e}")
    
    def _build_outline_prompt(self, title: str, description: str, keywords: str, target_audience: str) -> str:
        """Build the prompt for outline generation"""
        prompt = f"""Create a comprehensive content outline for the following article:

Title: {title}
Description: {description}
Keywords: {keywords}
Target Audience: {target_audience}

Generate a detailed outline that includes:
1. A compelling introduction hook
2. 5-7 main sections with descriptive subheadings
3. Key points to cover in each section
4. A conclusion that summarizes key takeaways
5. Suggested FAQ section (3-5 questions)

The outline should be optimized for:
- SEO and keyword integration
- E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) principles
- Reader engagement and value
- Comprehensive coverage of the topic

Format the outline clearly with numbered sections and bullet points for key details."""
        
        return prompt