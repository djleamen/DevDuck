"""
Security configuration for DevDuck VAPI integration.

Ensures HTTPS/WSS protocols are used for all external communications.
"""

import os
import logging
from typing import Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Manages security settings for URLs and protocols."""
    def __init__(self, force_https: bool = True):
        self.force_https = force_https
        self.allowed_local_hosts = ['localhost', '127.0.0.1', '::1']

    def _is_local_url(self, parsed_url) -> bool:
        return any(host in parsed_url.netloc for host in self.allowed_local_hosts)

    def _validate_websocket_protocol(self, parsed_url, is_local: bool, allow_local_http: bool) -> bool:
        """Validate WebSocket protocol."""
        if parsed_url.scheme == 'ws':
            if is_local and allow_local_http:
                logger.warning(
                    "Using insecure WebSocket for local URL: %s", parsed_url.geturl())
                return True
            logger.error(
                "Insecure WebSocket protocol not allowed: %s", parsed_url.geturl())
            return False
        return True

    def _validate_http_protocol(self, parsed_url, is_local: bool, allow_local_http: bool) -> bool:
        """Validate HTTP/HTTPS protocol."""
        if parsed_url.scheme == 'http':
            if is_local and allow_local_http:
                logger.warning("Using HTTP for local URL: %s",
                               parsed_url.geturl())
                return True
            logger.error(
                "HTTP protocol not allowed for external URL: %s", parsed_url.geturl())
            return False
        return True

    def validate_url(self, url: str, allow_local_http: bool = False) -> bool:
        """Validate a given URL for security compliance."""
        try:
            parsed = urlparse(url)
            is_local = self._is_local_url(parsed)

            if parsed.scheme in ['ws', 'wss']:
                return self._validate_websocket_protocol(parsed, is_local, allow_local_http)
            elif parsed.scheme in ['http', 'https']:
                return self._validate_http_protocol(parsed, is_local, allow_local_http)
            else:
                logger.error("Unsupported protocol: %s", parsed.scheme)
                return False

        except ValueError as e:
            logger.error("Error validating URL %s: %s", url, e)
            return False

    def secure_url(self, url: str) -> str:
        """Convert URL to secure protocol if needed."""
        try:
            if url.startswith('http://'):
                secure_url = url.replace('http://', 'https://', 1)
                logger.info("Converted HTTP to HTTPS: %s -> %s",
                            url, secure_url)
                return secure_url
            elif url.startswith('ws://'):
                secure_url = url.replace('ws://', 'wss://', 1)
                logger.info("Converted WS to WSS: %s -> %s", url, secure_url)
                return secure_url
            return url
        except ValueError as e:
            logger.error("Error securing URL %s: %s", url, e)
            return url

    def get_secure_config(self) -> Dict[str, Any]:
        """Get security settings for various components."""
        is_production = os.getenv('NODE_ENV') == 'production'

        return {
            'vapi': {
                'base_url': 'https://api.vapi.ai',
                'websocket_url': 'wss://api.vapi.ai',
                'force_https': is_production or self.force_https
            },
            'webhook': {
                'require_https': is_production or self.force_https,
                'allow_local_http': not is_production
            },
            'frontend': {
                'backend_url': 'https://localhost:8001' if is_production else 'http://localhost:8001',
                'secure_socket': is_production,
                'reject_unauthorized': is_production
            },
            'general': {
                'force_https': is_production or self.force_https,
                'allow_local_insecure': not is_production
            }
        }

    def validate_webhook_url(self, webhook_url: str) -> bool:
        """Validate the webhook URL for security compliance."""
        if not webhook_url or webhook_url == os.getenv("VAPI_WEBHOOK_URL"):
            logger.error("Webhook URL not configured")
            return False

        allow_local = os.getenv('NODE_ENV') != 'production'

        if not self.validate_url(webhook_url, allow_local_http=allow_local):
            return False

        if not webhook_url.endswith('/webhook/vapi'):
            logger.warning(
                "Webhook URL doesn't end with expected path: %s", webhook_url)

        return True


def get_security_config() -> SecurityConfig:
    """Get global security configuration."""
    force_https = os.getenv('DEVDUCK_FORCE_HTTPS', 'true').lower() == 'true'
    return SecurityConfig(force_https=force_https)


FORCE_HTTPS = os.getenv('DEVDUCK_FORCE_HTTPS', 'true').lower() == 'true'

SECURITY_CONFIG = get_security_config()
