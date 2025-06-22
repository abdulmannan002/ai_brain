"""
NLP service - Natural language processing for idea analysis
"""
from typing import Dict, Any, Optional
import spacy
from ..core.config import settings


class NLPService:
    """Service for NLP operations on ideas"""
    
    def __init__(self):
        self.nlp = None
        self._load_model()
    
    def _load_model(self):
        """Load spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback to basic English model
            self.nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
    
    async def analyze_idea(self, content: str) -> Dict[str, Any]:
        """Analyze idea content using NLP"""
        if not self.nlp:
            return self._fallback_analysis(content)
        
        doc = self.nlp(content)
        
        # Extract key information
        analysis = {
            "project": self._extract_project(doc),
            "theme": self._extract_theme(doc),
            "emotion": self._extract_emotion(doc),
            "keywords": self._extract_keywords(doc),
            "entities": self._extract_entities(doc),
            "sentiment": self._analyze_sentiment(doc)
        }
        
        return analysis
    
    def _extract_project(self, doc) -> Optional[str]:
        """Extract project name from content"""
        # Look for project-related patterns
        project_keywords = ["project", "app", "website", "platform", "system", "tool"]
        
        for token in doc:
            if token.text.lower() in project_keywords:
                # Look for the next noun phrase
                for child in token.children:
                    if child.pos_ in ["NOUN", "PROPN"]:
                        return child.text.title()
        
        return None
    
    def _extract_theme(self, doc) -> Optional[str]:
        """Extract theme from content"""
        # Look for theme-related patterns
        theme_keywords = ["about", "focus", "topic", "subject", "area"]
        
        for token in doc:
            if token.text.lower() in theme_keywords:
                # Look for the next noun phrase
                for child in token.children:
                    if child.pos_ in ["NOUN", "PROPN"]:
                        return child.text.title()
        
        return None
    
    def _extract_emotion(self, doc) -> Optional[str]:
        """Extract emotion from content"""
        # Simple emotion detection based on keywords
        emotion_keywords = {
            "excited": ["excited", "thrilled", "amazing", "awesome", "fantastic"],
            "happy": ["happy", "joy", "pleased", "satisfied", "content"],
            "curious": ["curious", "interested", "wonder", "explore", "discover"],
            "concerned": ["worried", "concerned", "anxious", "nervous", "stress"],
            "frustrated": ["frustrated", "annoyed", "irritated", "angry", "mad"]
        }
        
        text_lower = doc.text.lower()
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion
        
        return None
    
    def _extract_keywords(self, doc) -> list[str]:
        """Extract important keywords"""
        keywords = []
        
        for token in doc:
            if (token.pos_ in ["NOUN", "PROPN", "ADJ"] and 
                not token.is_stop and 
                len(token.text) > 2):
                keywords.append(token.text.lower())
        
        # Return top 5 keywords
        return keywords[:5]
    
    def _extract_entities(self, doc) -> list[str]:
        """Extract named entities"""
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return entities
    
    def _analyze_sentiment(self, doc) -> str:
        """Analyze sentiment of the content"""
        # Simple sentiment analysis based on positive/negative words
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "perfect"]
        negative_words = ["bad", "terrible", "awful", "horrible", "worst", "problem"]
        
        text_lower = doc.text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback analysis when spaCy is not available"""
        return {
            "project": None,
            "theme": None,
            "emotion": None,
            "keywords": content.split()[:5],
            "entities": [],
            "sentiment": "neutral"
        }
    
    async def categorize_idea(self, content: str) -> Dict[str, str]:
        """Categorize idea into project, theme, and emotion"""
        analysis = await self.analyze_idea(content)
        
        return {
            "project": analysis.get("project"),
            "theme": analysis.get("theme"),
            "emotion": analysis.get("emotion")
        }


# Global NLP service instance
nlp_service = NLPService() 