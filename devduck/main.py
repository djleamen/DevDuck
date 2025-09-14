"""
DevDuck Main Application

Simplified main application that coordinates the API server and basic functionality.
"""


import asyncio
import logging
# For audio sentiment listener
import threading
import time
from typing import Optional

from devduck.ai import VAPIClient
from devduck.analysis import analyze_developer_mood
from devduck.hardware.usb_communication import trigger_movement

try:
    import speech_recognition as sr
except ImportError:
    sr = None

logger = logging.getLogger(__name__)

class DevDuckApplication:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo_key"
        self.vapi_client = VAPIClient(self.api_key)
        self.is_running = False
        logger.info("DevDuck application initialized")
        self.sentiment_thread = None
        self._sentiment_running = False

    def start(self) -> bool:
        try:
            self.is_running = True
            success = self.vapi_client.start_conversation()
            if success:
                logger.info("DevDuck application started successfully")
                self.vapi_client.add_to_history(
                    "system", {"event": "application_started"})
                self.start_sentiment_listener()
            return success
        except Exception as e:
            logger.error("Failed to start DevDuck application: %s", e)
            return False

    def stop(self) -> bool:
        try:
            self.is_running = False
            self.stop_sentiment_listener()
            success = self.vapi_client.stop_conversation()
            if success:
                logger.info("DevDuck application stopped")
                self.vapi_client.add_to_history(
                    "system", {"event": "application_stopped"})
            return success
        except Exception as e:
            logger.error("Failed to stop DevDuck application: %s", e)
            return False
    # --- Sentiment Audio Listener ---
    def start_sentiment_listener(self):
        if sr is None:
            logger.warning("speech_recognition not installed; sentiment listener disabled.")
            return
        if self.sentiment_thread and self.sentiment_thread.is_alive():
            logger.info("Sentiment listener already running.")
            return
        self._sentiment_running = True
        self.sentiment_thread = threading.Thread(target=self._sentiment_audio_loop, daemon=True)
        self.sentiment_thread.start()
        logger.info("Sentiment audio listener started.")

    def stop_sentiment_listener(self):
        self._sentiment_running = False
        if self.sentiment_thread:
            self.sentiment_thread.join(timeout=2)
            logger.info("Sentiment audio listener stopped.")

    def _sentiment_audio_loop(self):
        if sr is None:
            logger.warning("speech_recognition not installed; cannot run sentiment audio loop.")
            return
        try:
            recognizer = sr.Recognizer()
            mic = sr.Microphone()
        except Exception as e:
            logger.error("[Sentiment Listener] Could not initialize recognizer or mic: %s", e)
            return
        logger.info("Sentiment audio loop running.")
        while self._sentiment_running:
            try:
                with mic as source:
                    logger.debug("[Sentiment Listener] Listening for sentiment audio...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    logger.debug("[Sentiment Listener] Audio captured.")
                try:
                    text = recognizer.recognize_google(audio)  # type: ignore
                    logger.info("[Sentiment Listener] Transcription: %s", text)
                except Exception as e:
                    logger.error("[Sentiment Listener] Speech-to-text failed: %s", e)
                    text = None
                if text:
                    logger.debug("[Sentiment Listener] Running sentiment analysis on: %s", text)
                    sentiment_result = analyze_developer_mood(text)
                    logger.info("[Sentiment Listener] Sentiment result: %s", sentiment_result)
                    movement = sentiment_result.get('movement')
                    if movement:
                        logger.info("[Sentiment Listener] About to trigger duck movement: %s", movement)
                        trigger_movement(movement)
                        logger.debug(f"Triggered duck movement: {movement}")
                        logger.info("[Sentiment Listener] Triggered duck movement: %s", movement)
                    else:
                        logger.info("[Sentiment Listener] No movement detected for this sentiment.")
            except Exception as e:
                logger.error("[Sentiment Listener] Outer loop error: %s", e)
            time.sleep(1)

    def process_user_input(self, text: str) -> dict:
        # Analyze sentiment and trigger duck movement
        sentiment_result = analyze_developer_mood(text)
        movement = sentiment_result.get('movement')
        if movement:
            trigger_movement(movement)
            logger.debug(f"Triggered duck movement: {movement}")
            logger.info("Triggered duck movement: %s", movement)
        sentiment = sentiment_result.get('sentiment', 'unknown')
        response = f"Sentiment: {sentiment.capitalize()}"
        return {
            "response": response,
            "sentiment": sentiment_result.get('sentiment'),
            "confidence": sentiment_result.get('confidence'),
            "movement": movement
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