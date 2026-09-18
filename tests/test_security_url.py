from urllib.parse import urlparse

import pytest

from devduck.utils.security import SecurityConfig


@pytest.fixture
def config():
    return SecurityConfig(force_https=True)


@pytest.mark.parametrize(
    "netloc",
    ["localhost:8001", "127.0.0.1", "[::1]:9000"],
)
def test_local_hosts_are_recognised(config, netloc):
    parsed = urlparse(f"http://{netloc}/path")
    assert config._is_local_url(parsed) is True


@pytest.mark.parametrize(
    "host",
    [
        "localhost.attacker.com",
        "127.0.0.1.evil.com",
        "api.vapi.ai",
        "example.com",
    ],
)
def test_spoofed_and_external_hosts_are_not_local(config, host):
    # A substring match on netloc would wrongly treat the first two as local.
    parsed = urlparse(f"http://{host}/path")
    assert config._is_local_url(parsed) is False


def test_local_http_allowed_only_when_opted_in(config):
    assert config.validate_url("http://localhost:8001", allow_local_http=True) is True
    assert config.validate_url("http://localhost:8001", allow_local_http=False) is False


def test_local_websocket_allowed_only_when_opted_in(config):
    assert config.validate_url("ws://[::1]:9000", allow_local_http=True) is True
    assert config.validate_url("ws://[::1]:9000", allow_local_http=False) is False


def test_spoofed_local_host_cannot_use_insecure_http(config):
    # The key regression: a host that merely contains "localhost" must not be
    # allowed to fall through the local-insecure path.
    assert (
        config.validate_url("http://localhost.attacker.com", allow_local_http=True)
        is False
    )
    assert (
        config.validate_url("http://127.0.0.1.evil.com", allow_local_http=True)
        is False
    )


def test_secure_external_urls_pass(config):
    assert config.validate_url("https://api.vapi.ai") is True
    assert config.validate_url("wss://api.vapi.ai") is True
