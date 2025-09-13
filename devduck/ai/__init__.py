"""
Simplified VAPI integration for DevDuck.
"""

import logging
from typing import Optional, Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    ERROR = "error"


class VAPIClient:
    """Simplified VAPI client for basic conversation management."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.is_connected = False
        self.conversation_state = ConversationState.IDLE
        self.conversation_history: List[Dict[str, Any]] = []
        logger.info("VAPI client initialized")

    def start_conversation(self) -> bool:
        """Start a new conversation session."""
        try:
            self.conversation_state = ConversationState.LISTENING
            self.is_connected = True
            logger.info("Conversation started")
            return True
        except Exception as e:
            logger.error("Failed to start conversation: %s", e)
            self.conversation_state = ConversationState.ERROR
            return False

    def stop_conversation(self) -> bool:
        """Stop the current conversation."""
        try:
            self.conversation_state = ConversationState.IDLE
            self.is_connected = False
            logger.info("Conversation stopped")
            return True
        except Exception as e:
            logger.error("Failed to stop conversation: %s", e)
            return False

    def get_state(self) -> Dict[str, Any]:
        """Get current client state."""
        return {
            "is_connected": self.is_connected,
            "conversation_state": self.conversation_state.value
        }

    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def add_to_history(self, event_type: str, data: Any) -> None:
        """Add an event to conversation history."""
        from datetime import datetime, timezone
        self.conversation_history.append({
            'type': event_type,
            'data': data,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
