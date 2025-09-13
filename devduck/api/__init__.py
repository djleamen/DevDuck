"""
DevDuck API module for external integrations.
"""

from .vapi_webhook import app as webhook_app

__all__ = ["webhook_app"]