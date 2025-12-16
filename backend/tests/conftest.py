"""Pytest configuration and fixtures for GroundedCV tests."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add the app directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("app.config.settings") as mock:
        mock.model_fast = "claude-3-5-haiku-20241022"
        mock.model_balanced = "claude-sonnet-4-5-20250929"
        mock.model_reasoning = "claude-opus-4-5-20251101"
        mock.max_tokens = 4096
        mock.max_iterations = 10
        mock.data_dir = Path("./data")
        yield mock


@pytest.fixture
def mock_text_block():
    """Create a mock TextBlock from claude-agent-sdk."""
    block = MagicMock()
    block.text = "Test response from Claude"
    return block


@pytest.fixture
def mock_assistant_message(mock_text_block):
    """Create a mock AssistantMessage from claude-agent-sdk."""
    message = MagicMock()
    message.content = [mock_text_block]
    return message


@pytest.fixture
def mock_result_message():
    """Create a mock ResultMessage from claude-agent-sdk."""
    message = MagicMock()
    message.usage = {"input_tokens": 100, "output_tokens": 50}
    message.duration_ms = 1500
    message.total_cost_usd = 0.0025
    message.session_id = "test-session-123"
    return message


@pytest.fixture
def mock_query(mock_assistant_message, mock_result_message):
    """Mock the query function from claude-agent-sdk."""

    async def mock_query_fn(*args, **kwargs):
        yield mock_assistant_message
        yield mock_result_message

    return mock_query_fn


@pytest.fixture
def mock_sdk_client():
    """Mock ClaudeSDKClient from claude-agent-sdk."""
    client = AsyncMock()
    client.connect = AsyncMock()
    client.query = AsyncMock()
    client.receive_response = AsyncMock()
    client.disconnect = AsyncMock()
    return client
