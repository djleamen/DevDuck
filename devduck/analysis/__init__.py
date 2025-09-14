"""
Simplified analysis module for DevDuck.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SentimentType(Enum):
    """Enum for sentiment types."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class BasicSentimentAnalyzer:
    """Basic sentiment analysis for developer mood detection."""
    
    def __init__(self):
        self.positive_keywords = ['good', 'great', 'excellent', 'working', 'fixed', 'solved']
        self.negative_keywords = ['error', 'bug', 'broken', 'stuck', 'frustrated', 'problem']
        logger.info("Basic sentiment analyzer initialized")

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment from text and suggest duck movement action."""
        if not text:
            return {
                'sentiment': SentimentType.NEUTRAL.value,
                'confidence': 0.0,
                'movement': 'nod'  # Default to nod for neutral/no input
            }

        text_lower = text.lower()
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)

        if positive_count > negative_count:
            sentiment = SentimentType.POSITIVE
            confidence = min(0.8, positive_count * 0.2)
            movement = 'dance'  # Happy/positive
        elif negative_count > positive_count:
            sentiment = SentimentType.NEGATIVE
            confidence = min(0.8, negative_count * 0.2)
            movement = 'shake'  # Disagreement/negative
        else:
            sentiment = SentimentType.NEUTRAL
            confidence = 0.5
            movement = 'nod'  # Neutral/agreement

        return {
            'sentiment': sentiment.value,
            'confidence': confidence,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'movement': movement
        }


def analyze_developer_mood(text: str) -> Dict[str, Any]:
    """Quick function to analyze developer mood from text."""
    analyzer = BasicSentimentAnalyzer()
    return analyzer.analyze_text(text)
