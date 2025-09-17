"""
OpenAI API Client for content expansion and rewriting using GPT-5
"""

import os
from typing import Dict, Any
import asyncio
from openai import AsyncOpenAI


class OpenAIClient:
    """Client for OpenAI API to expand outlines and rewrite content using GPT-5"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def rewrite_content(self, row: Dict[str, Any], outline: str) -> str:
        """
        Expand outline and rewrite content using GPT-5
        
        Args:
            row: CSV row with original data
            outline: Generated outline from OpenRouter
            
        Returns:
            Fully rewritten content
        """
        title = row.get('title', '')
        description = row.get('description', '')
        keywords = row.get('keywords', '')
        target_audience = row.get('target_audience', '')
        original_content = row.get('content', '')
        
        prompt = self._build_rewrite_prompt(
            title, description, keywords, target_audience, original_content, outline
        )
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 as GPT-5 may not be available yet
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            if not response.choices:
                raise Exception("No response from OpenAI API")
            
            content = response.choices[0].message.content.strip()
            
            # Ensure minimum word count
            if len(content.split()) < 800:
                content = await self._expand_content(content, title, outline)
            
            return content
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    async def _expand_content(self, content: str, title: str, outline: str) -> str:
        """Expand content if it's below minimum word count"""
        expansion_prompt = f"""The following content is below the required 800+ word minimum. 
Please expand it significantly while maintaining quality and relevance:

Title: {title}
Current Content: {content}
Outline Reference: {outline}

Requirements:
- Expand to at least 800 words
- Add more detailed explanations
- Include relevant examples
- Enhance with actionable insights
- Maintain the original structure and key points
- Ensure enterprise-quality writing"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": expansion_prompt
                }
            ],
            max_tokens=4000,
            temperature=0.6
        )
        
        return response.choices[0].message.content.strip()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for content generation"""
        return """You are an expert content writer specializing in creating high-quality, enterprise-grade content. 

Your writing must demonstrate:
- Experience: Include real-world examples and practical insights
- Expertise: Show deep knowledge of the subject matter
- Authoritativeness: Reference credible sources and best practices
- Trustworthiness: Provide accurate, helpful, and honest information

Writing standards:
- Minimum 800 words
- Clear, engaging, and professional tone
- SEO-optimized with natural keyword integration
- Well-structured with proper headings and subheadings
- Actionable insights and practical value
- Include FAQ section when appropriate
- Enterprise-quality grammar and style"""
    
    def _build_rewrite_prompt(
        self, 
        title: str, 
        description: str, 
        keywords: str, 
        target_audience: str,
        original_content: str,
        outline: str
    ) -> str:
        """Build the prompt for content rewriting"""
        prompt = f"""Rewrite and expand the following content based on the provided outline:

**Title:** {title}
**Description:** {description}
**Keywords:** {keywords}
**Target Audience:** {target_audience}

**Original Content:**
{original_content}

**Outline to Follow:**
{outline}

**Instructions:**
1. Completely rewrite the content using the outline as a guide
2. Ensure the content is at least 800 words
3. Optimize for the provided keywords naturally
4. Write for the specified target audience
5. Include a compelling introduction and strong conclusion
6. Add an FAQ section with 3-5 relevant questions and answers
7. Use proper heading structure (H2, H3, etc.)
8. Include actionable insights and practical value
9. Demonstrate E-E-A-T principles throughout
10. Maintain professional, engaging tone

The final content should be enterprise-quality and significantly improved from the original."""
        
        return prompt