"""
Transform service - AI-powered idea transformations
"""
from typing import Dict, Any, Optional
import httpx
from ..core.config import settings
from ..models.transform import TransformRequest, TransformResponse


class TransformService:
    """Service for AI-powered idea transformations"""
    
    def __init__(self):
        self.xai_api_key = settings.ai_api.xai_api_key
        self.xai_api_url = settings.ai_api.xai_api_url
        self.openai_api_key = settings.ai_api.openai_api_key
    
    async def transform_idea(self, request: TransformRequest) -> TransformResponse:
        """Transform idea using AI"""
        # Get the original idea content
        from ..services.idea_service import idea_service
        idea = await idea_service.get_idea_by_id(request.idea_id, request.user_id)
        
        if not idea:
            raise ValueError("Idea not found")
        
        # Generate transformation based on output type
        if request.output_type == "content":
            transformed_content = await self._generate_content(idea.content)
        elif request.output_type == "ip":
            transformed_content = await self._generate_ip_content(idea.content)
        elif request.output_type == "tasks":
            transformed_content = await self._generate_tasks(idea.content)
        else:
            raise ValueError(f"Unknown output type: {request.output_type}")
        
        # Update the idea with transformed output
        from ..models.idea import IdeaUpdate
        update_data = IdeaUpdate(transformed_output=transformed_content)
        await idea_service.update_idea(request.idea_id, request.user_id, update_data)
        
        return TransformResponse(
            transformed_content=transformed_content,
            idea_id=request.idea_id,
            output_type=request.output_type
        )
    
    async def _generate_content(self, idea_content: str) -> str:
        """Generate content from idea"""
        prompt = f"""
        Transform this idea into engaging content:
        
        Original idea: {idea_content}
        
        Please create compelling content that expands on this idea, making it more detailed and engaging for readers.
        """
        
        return await self._call_ai_api(prompt)
    
    async def _generate_ip_content(self, idea_content: str) -> str:
        """Generate intellectual property content from idea"""
        prompt = f"""
        Transform this idea into intellectual property content:
        
        Original idea: {idea_content}
        
        Please create detailed intellectual property content including:
        - Patentable concepts
        - Copyrightable material
        - Trademark considerations
        - Trade secret elements
        """
        
        return await self._call_ai_api(prompt)
    
    async def _generate_tasks(self, idea_content: str) -> str:
        """Generate actionable tasks from idea"""
        prompt = f"""
        Transform this idea into actionable tasks:
        
        Original idea: {idea_content}
        
        Please break down this idea into specific, actionable tasks that can be executed to bring this idea to life.
        Include timelines, priorities, and resource requirements.
        """
        
        return await self._call_ai_api(prompt)
    
    async def _call_ai_api(self, prompt: str) -> str:
        """Call AI API for content generation"""
        if self.xai_api_key:
            return await self._call_xai_api(prompt)
        elif self.openai_api_key:
            return await self._call_openai_api(prompt)
        else:
            return self._fallback_generation(prompt)
    
    async def _call_xai_api(self, prompt: str) -> str:
        """Call X.AI API (LLaMA 3)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.xai_api_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.xai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3-70b",
                        "messages": [
                            {"role": "system", "content": "You are an AI assistant that helps transform ideas into actionable content."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return self._fallback_generation(prompt)
                    
        except Exception:
            return self._fallback_generation(prompt)
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API as fallback"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You are an AI assistant that helps transform ideas into actionable content."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return self._fallback_generation(prompt)
                    
        except Exception:
            return self._fallback_generation(prompt)
    
    def _fallback_generation(self, prompt: str) -> str:
        """Fallback content generation when AI APIs are not available"""
        # Simple template-based generation
        if "content" in prompt.lower():
            return "This is a generated content based on your idea. In a production environment, this would be enhanced by AI-powered content generation."
        elif "ip" in prompt.lower():
            return "Intellectual Property Analysis:\n- Patent considerations\n- Copyright elements\n- Trademark opportunities\n- Trade secret aspects"
        elif "tasks" in prompt.lower():
            return "Actionable Tasks:\n1. Research and validate the idea\n2. Create a detailed plan\n3. Identify required resources\n4. Set milestones and timelines"
        else:
            return "Transformed content based on your idea. AI enhancement would provide more detailed and contextual output."


# Global transform service instance
transform_service = TransformService() 