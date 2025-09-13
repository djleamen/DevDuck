"""
DevDuck Main Application

Simplified main application that coordinates the API server and basic functionality.
"""

import asyncio
import logging
from typing import Optional

from devduck.ai import VAPIClient
from devduck.analysis import BasicSentimentAnalyzer

logger = logging.getLogger(__name__)

class DevDuckApplication:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo_key"
        self.vapi_client = VAPIClient(self.api_key)
        self.sentiment_analyzer = BasicSentimentAnalyzer()
        self.is_running = False
        logger.info("DevDuck application initialized")

    def start(self) -> bool:
        try:
            self.is_running = True
            success = self.vapi_client.start_conversation()
            if success:
                logger.info("DevDuck application started successfully")
                self.vapi_client.add_to_history(
                    "system", {"event": "application_started"})
            return success
        except Exception as e:
            logger.error("Failed to start DevDuck application: %s", e)
            return False

    def stop(self) -> bool:
        try:
            self.is_running = False
            success = self.vapi_client.stop_conversation()
            if success:
                logger.info("DevDuck application stopped")
                self.vapi_client.add_to_history(
                    "system", {"event": "application_stopped"})
            return success
        except Exception as e:
            logger.error("Failed to stop DevDuck application: %s", e)
            return False

    def process_user_input(self, text: str) -> dict:
        sentiment_result = self.sentiment_analyzer.analyze_text(text)

        self.vapi_client.add_to_history("user_input", {
            "text": text,
            "sentiment": sentiment_result
        })

        if sentiment_result['sentiment'] == 'negative':
            response = "I understand you're facing some challenges. Let's work through this together!"
        elif sentiment_result['sentiment'] == 'positive':
            response = "Great to hear things are going well! Keep up the good work!"
        else:
            response = "I'm here to help with whatever you're working on."

        self.vapi_client.add_to_history("assistant_response", {
            "text": response,
            "user_sentiment": sentiment_result
        })

        return {
            "response": response,
            "sentiment": sentiment_result,
            "conversation_state": self.vapi_client.get_state()
        }

    def get_status(self) -> dict:
        return {
            "is_running": self.is_running,
            "vapi_state": self.vapi_client.get_state(),
            "conversation_history_count": len(self.vapi_client.get_history())
        }

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def main():
    setup_logging()
    app = DevDuckApplication()
    if app.start():
        logger.info("DevDuck is running!")
        try:
            while app.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down DevDuck...")
            app.stop()
    else:
        logger.error("Failed to start DevDuck application")

if __name__ == "__main__":
    asyncio.run(main())
