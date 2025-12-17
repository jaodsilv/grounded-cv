"""Unit tests for BaseAgent with claude-agent-sdk integration."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock


class TestAgentMetadata:
    """Tests for AgentMetadata dataclass."""

    def test_metadata_initialization(self):
        """Test AgentMetadata can be initialized with required fields."""
        from app.agents.base import AgentMetadata

        metadata = AgentMetadata(
            agent_name="test-agent",
            model_used="claude-sonnet-4-5-20250929",
        )

        assert metadata.agent_name == "test-agent"
        assert metadata.model_used == "claude-sonnet-4-5-20250929"
        assert metadata.tokens_in == 0
        assert metadata.tokens_out == 0
        assert metadata.latency_ms == 0
        assert metadata.cost_usd == 0.0
        assert metadata.session_id is None

    def test_metadata_from_result_message(self):
        """Test creating AgentMetadata from SDK ResultMessage."""
        from app.agents.base import AgentMetadata

        # Mock a ResultMessage from claude-agent-sdk
        mock_result = MagicMock()
        mock_result.usage = {"input_tokens": 100, "output_tokens": 50}
        mock_result.duration_ms = 1500
        mock_result.total_cost_usd = 0.0025
        mock_result.session_id = "test-session-123"

        started_at = datetime.now()

        metadata = AgentMetadata.from_result_message(
            agent_name="test-agent",
            model="claude-sonnet-4-5-20250929",
            result=mock_result,
            started_at=started_at,
        )

        assert metadata.agent_name == "test-agent"
        assert metadata.model_used == "claude-sonnet-4-5-20250929"
        assert metadata.tokens_in == 100
        assert metadata.tokens_out == 50
        assert metadata.latency_ms == 1500
        assert metadata.cost_usd == 0.0025
        assert metadata.session_id == "test-session-123"
        assert metadata.started_at == started_at
        assert metadata.completed_at is not None

    def test_calculate_cost_fallback(self):
        """Test manual cost calculation as fallback."""
        from app.agents.base import AgentMetadata

        metadata = AgentMetadata(
            agent_name="test-agent",
            model_used="claude-sonnet-4-5-20250929",
            tokens_in=1000,
            tokens_out=500,
        )

        cost = metadata.calculate_cost()

        # Sonnet pricing: $0.003/1K input, $0.015/1K output
        expected_cost = (1000 / 1000) * 0.003 + (500 / 1000) * 0.015
        assert cost == pytest.approx(expected_cost)


class TestAgentResponse:
    """Tests for AgentResponse dataclass."""

    def test_response_success(self):
        """Test creating a success response."""
        from app.agents.base import AgentMetadata, AgentResponse

        metadata = AgentMetadata(
            agent_name="test-agent",
            model_used="claude-sonnet-4-5-20250929",
        )

        response = AgentResponse(
            status="success",
            output={"result": "test output"},
            metadata=metadata,
        )

        assert response.status == "success"
        assert response.output == {"result": "test output"}
        assert response.errors == []

    def test_response_error(self):
        """Test creating an error response."""
        from app.agents.base import AgentMetadata, AgentResponse

        metadata = AgentMetadata(
            agent_name="test-agent",
            model_used="claude-sonnet-4-5-20250929",
        )

        response = AgentResponse(
            status="error",
            output=None,
            metadata=metadata,
            errors=["Something went wrong"],
        )

        assert response.status == "error"
        assert response.errors == ["Something went wrong"]


class TestBaseAgentInitialization:
    """Tests for BaseAgent initialization."""

    def test_default_initialization(self, mock_settings):
        """Test BaseAgent initializes with default values."""
        from app.agents.base import BaseAgent

        # Create a concrete subclass for testing
        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        with patch("app.agents.base.settings", mock_settings):
            agent = TestAgent(name="test-agent")

            assert agent.name == "test-agent"
            assert agent.model == "claude-sonnet-4-5-20250929"
            assert agent.tools == BaseAgent.DEFAULT_TOOLS
            assert agent.system_prompt is None
            assert agent._client is None

    def test_custom_initialization(self, mock_settings):
        """Test BaseAgent initializes with custom values."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        with patch("app.agents.base.settings", mock_settings):
            agent = TestAgent(
                name="custom-agent",
                model="claude-opus-4-5-20251101",
                tools=["Read", "Grep"],
                system_prompt="You are a helpful assistant.",
            )

            assert agent.name == "custom-agent"
            assert agent.model == "claude-opus-4-5-20251101"
            assert agent.tools == ["Read", "Grep"]
            assert agent.system_prompt == "You are a helpful assistant."

    def test_default_tools_constant(self):
        """Test DEFAULT_TOOLS contains expected built-in tools."""
        from app.agents.base import BaseAgent

        expected_tools = [
            "Read",
            "Write",
            "Edit",
            "Bash",
            "Glob",
            "Grep",
            "WebSearch",
            "WebFetch",
        ]
        assert BaseAgent.DEFAULT_TOOLS == expected_tools


class TestBaseAgentStatelessAPI:
    """Tests for stateless API methods (_call_claude, _stream_claude)."""

    @pytest.mark.asyncio
    async def test_call_claude_returns_text_and_metadata(self, mock_settings):
        """Test _call_claude returns response text and metadata."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        # Mock the query function using spec to pass isinstance checks
        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "Hello, this is Claude!"

        mock_assistant = MagicMock(spec=AssistantMessage)
        mock_assistant.content = [mock_text_block]

        mock_result = MagicMock(spec=ResultMessage)
        mock_result.usage = {"input_tokens": 50, "output_tokens": 25}
        mock_result.duration_ms = 800
        mock_result.total_cost_usd = 0.001
        mock_result.session_id = "session-abc"

        async def mock_query(*args, **kwargs):
            yield mock_assistant
            yield mock_result

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query),
        ):
            agent = TestAgent(name="test-agent")
            text, metadata = await agent._call_claude("Hello Claude!")

            assert text == "Hello, this is Claude!"
            assert metadata.tokens_in == 50
            assert metadata.tokens_out == 25
            assert metadata.cost_usd == 0.001
            assert metadata.session_id == "session-abc"

    @pytest.mark.asyncio
    async def test_stream_claude_yields_text_chunks(self, mock_settings):
        """Test _stream_claude yields text chunks."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        # Mock streaming response with multiple text blocks using spec
        mock_block1 = MagicMock(spec=TextBlock)
        mock_block1.text = "First "

        mock_block2 = MagicMock(spec=TextBlock)
        mock_block2.text = "chunk "

        mock_block3 = MagicMock(spec=TextBlock)
        mock_block3.text = "here!"

        mock_assistant1 = MagicMock(spec=AssistantMessage)
        mock_assistant1.content = [mock_block1]

        mock_assistant2 = MagicMock(spec=AssistantMessage)
        mock_assistant2.content = [mock_block2]

        mock_assistant3 = MagicMock(spec=AssistantMessage)
        mock_assistant3.content = [mock_block3]

        mock_result = MagicMock(spec=ResultMessage)
        mock_result.usage = {"input_tokens": 10, "output_tokens": 5}
        mock_result.duration_ms = 500
        mock_result.total_cost_usd = 0.0005
        mock_result.session_id = "stream-session"

        async def mock_query(*args, **kwargs):
            yield mock_assistant1
            yield mock_assistant2
            yield mock_assistant3
            yield mock_result

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query),
        ):
            agent = TestAgent(name="test-agent")
            chunks = []
            async for chunk in agent._stream_claude("Stream test"):
                chunks.append(chunk)

            assert chunks == ["First ", "chunk ", "here!"]


class TestBaseAgentConversationalAPI:
    """Tests for conversational API methods."""

    @pytest.mark.asyncio
    async def test_start_conversation(self, mock_settings, mock_sdk_client):
        """Test _start_conversation initializes client."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.ClaudeSDKClient", return_value=mock_sdk_client),
        ):
            agent = TestAgent(name="test-agent")
            assert agent._client is None

            await agent._start_conversation(initial_prompt="Hello")

            assert agent._client is not None
            mock_sdk_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_continue_conversation_without_starting_raises(self, mock_settings):
        """Test _continue_conversation raises if no session started."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        with patch("app.agents.base.settings", mock_settings):
            agent = TestAgent(name="test-agent")

            with pytest.raises(RuntimeError, match="No active conversation"):
                await agent._continue_conversation("Hello")

    @pytest.mark.asyncio
    async def test_end_conversation(self, mock_settings, mock_sdk_client):
        """Test _end_conversation disconnects client."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.ClaudeSDKClient", return_value=mock_sdk_client),
        ):
            agent = TestAgent(name="test-agent")
            await agent._start_conversation()
            assert agent._client is not None

            await agent._end_conversation()

            assert agent._client is None
            mock_sdk_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_settings, mock_sdk_client):
        """Test async context manager starts and ends conversation."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.ClaudeSDKClient", return_value=mock_sdk_client),
        ):
            agent = TestAgent(name="test-agent")

            async with agent:
                assert agent._client is not None
                mock_sdk_client.connect.assert_called_once()

            assert agent._client is None
            mock_sdk_client.disconnect.assert_called_once()


class TestQuickQuery:
    """Tests for the quick_query helper function."""

    @pytest.mark.asyncio
    async def test_quick_query_returns_text(self, mock_settings):
        """Test quick_query returns response text."""
        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "Quick response!"

        mock_assistant = MagicMock(spec=AssistantMessage)
        mock_assistant.content = [mock_text_block]

        mock_result = MagicMock(spec=ResultMessage)
        mock_result.usage = {"input_tokens": 10, "output_tokens": 5}
        mock_result.duration_ms = 200
        mock_result.total_cost_usd = 0.0001
        mock_result.session_id = "quick-session"

        async def mock_query(*args, **kwargs):
            yield mock_assistant
            yield mock_result

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query),
        ):
            from app.agents.base import quick_query

            result = await quick_query("Quick question")

            assert result == "Quick response!"


class TestMissingCoverage:
    """Tests for previously uncovered code paths."""

    @pytest.mark.asyncio
    async def test_continue_conversation_success(self, mock_settings, mock_sdk_client):
        """Test _continue_conversation happy path with active client."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        # Mock text block and messages with spec for isinstance checks
        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "Continued response!"

        mock_assistant = MagicMock(spec=AssistantMessage)
        mock_assistant.content = [mock_text_block]

        mock_result = MagicMock(spec=ResultMessage)
        mock_result.usage = {"input_tokens": 30, "output_tokens": 20}
        mock_result.duration_ms = 600
        mock_result.total_cost_usd = 0.002
        mock_result.session_id = "continue-session"

        async def mock_receive_response():
            yield mock_assistant
            yield mock_result

        mock_sdk_client.receive_response = mock_receive_response

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.ClaudeSDKClient", return_value=mock_sdk_client),
        ):
            agent = TestAgent(name="test-agent")
            await agent._start_conversation()

            text, metadata = await agent._continue_conversation("Follow-up question")

            assert text == "Continued response!"
            assert metadata is not None
            assert metadata.tokens_in == 30
            assert metadata.tokens_out == 20
            assert metadata.cost_usd == 0.002
            mock_sdk_client.query.assert_called_once_with("Follow-up question")

    @pytest.mark.asyncio
    async def test_stream_conversation_yields_text(self, mock_settings, mock_sdk_client):
        """Test _stream_conversation yields text chunks with active client."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        # Mock streaming response
        mock_block1 = MagicMock(spec=TextBlock)
        mock_block1.text = "Stream "

        mock_block2 = MagicMock(spec=TextBlock)
        mock_block2.text = "chunks!"

        mock_assistant1 = MagicMock(spec=AssistantMessage)
        mock_assistant1.content = [mock_block1]

        mock_assistant2 = MagicMock(spec=AssistantMessage)
        mock_assistant2.content = [mock_block2]

        async def mock_receive_response():
            yield mock_assistant1
            yield mock_assistant2

        mock_sdk_client.receive_response = mock_receive_response

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.ClaudeSDKClient", return_value=mock_sdk_client),
        ):
            agent = TestAgent(name="test-agent")
            await agent._start_conversation()

            chunks = []
            async for chunk in agent._stream_conversation("Stream this"):
                chunks.append(chunk)

            assert chunks == ["Stream ", "chunks!"]
            mock_sdk_client.query.assert_called_once_with("Stream this")

    @pytest.mark.asyncio
    async def test_stream_conversation_without_starting_raises(self, mock_settings):
        """Test _stream_conversation raises if no session started."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        with patch("app.agents.base.settings", mock_settings):
            agent = TestAgent(name="test-agent")

            with pytest.raises(RuntimeError, match="No active conversation"):
                async for _ in agent._stream_conversation("Hello"):
                    pass

    @pytest.mark.asyncio
    async def test_call_claude_fallback_metadata(self, mock_settings):
        """Test _call_claude creates fallback metadata when no ResultMessage received."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        # Only yield AssistantMessage, no ResultMessage
        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "Response without result!"

        mock_assistant = MagicMock(spec=AssistantMessage)
        mock_assistant.content = [mock_text_block]

        async def mock_query_no_result(*args, **kwargs):
            yield mock_assistant
            # No ResultMessage yielded

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query_no_result),
        ):
            agent = TestAgent(name="test-agent")
            text, metadata = await agent._call_claude("Test prompt")

            assert text == "Response without result!"
            # Fallback metadata should have zeros
            assert metadata.tokens_in == 0
            assert metadata.tokens_out == 0
            assert metadata.cost_usd == 0.0
            assert metadata.agent_name == "test-agent"

    @pytest.mark.asyncio
    async def test_context_manager_cleanup_on_exception(self, mock_settings, mock_sdk_client):
        """Test context manager cleans up even when exception occurs."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.ClaudeSDKClient", return_value=mock_sdk_client),
        ):
            agent = TestAgent(name="test-agent")

            with pytest.raises(ValueError, match="Test error"):
                async with agent:
                    assert agent._client is not None
                    raise ValueError("Test error")

            # Cleanup should still have happened
            assert agent._client is None
            mock_sdk_client.disconnect.assert_called_once()


class TestBaseAgentRetry:
    """Tests for retry behavior in BaseAgent methods."""

    @pytest.mark.asyncio
    async def test_call_claude_retries_on_connection_error(self, mock_settings):
        """Test _call_claude retries on AgentConnectionError."""
        from app.agents.base import BaseAgent
        from app.utils.retry import RetryConfig

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        call_count = 0

        # Mock that fails once then succeeds
        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "Success after retry!"

        mock_assistant = MagicMock(spec=AssistantMessage)
        mock_assistant.content = [mock_text_block]

        mock_result = MagicMock(spec=ResultMessage)
        mock_result.usage = {"input_tokens": 10, "output_tokens": 5}
        mock_result.duration_ms = 100
        mock_result.total_cost_usd = 0.001
        mock_result.session_id = "retry-session"

        async def mock_query_fails_then_succeeds(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Temporary connection failure")
            yield mock_assistant
            yield mock_result

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query_fails_then_succeeds),
        ):
            mock_settings.retry_max_attempts = 3
            mock_settings.retry_base_delay = 0.01
            mock_settings.retry_max_delay = 0.1
            mock_settings.retry_exponential_base = 2.0

            agent = TestAgent(
                name="test-agent",
                retry_config=RetryConfig(
                    max_attempts=3,
                    base_delay=0.01,
                    jitter=False,
                ),
            )
            text, metadata = await agent._call_claude("Test prompt")

            assert text == "Success after retry!"
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_call_claude_no_retry_on_query_error(self, mock_settings):
        """Test _call_claude does NOT retry on AgentQueryError."""
        from app.agents.base import AgentQueryError, BaseAgent
        from app.utils.retry import RetryConfig

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        call_count = 0

        async def mock_query_raises_error(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Simulate a non-retryable error (not ConnectionError/TimeoutError/OSError)
            raise ValueError("Application-level error")
            yield  # Make it a generator

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query_raises_error),
        ):
            mock_settings.retry_max_attempts = 3
            mock_settings.retry_base_delay = 0.01
            mock_settings.retry_max_delay = 0.1
            mock_settings.retry_exponential_base = 2.0

            agent = TestAgent(
                name="test-agent",
                retry_config=RetryConfig(
                    max_attempts=3,
                    base_delay=0.01,
                    jitter=False,
                ),
            )

            with pytest.raises(AgentQueryError, match="Query to Claude failed"):
                await agent._call_claude("Test prompt")

            # Should NOT retry on AgentQueryError
            assert call_count == 1

    @pytest.mark.asyncio
    async def test_call_claude_exhausts_retries(self, mock_settings):
        """Test _call_claude raises after exhausting retry attempts."""
        from app.agents.base import AgentConnectionError, BaseAgent
        from app.utils.retry import RetryConfig

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        call_count = 0

        async def mock_query_always_fails(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Persistent connection failure")
            yield

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query_always_fails),
        ):
            agent = TestAgent(
                name="test-agent",
                retry_config=RetryConfig(
                    max_attempts=3,
                    base_delay=0.01,
                    jitter=False,
                ),
            )

            with pytest.raises(AgentConnectionError, match="Failed to connect"):
                await agent._call_claude("Test prompt")

            assert call_count == 3

    @pytest.mark.asyncio
    async def test_stream_claude_retries_on_initial_failure(self, mock_settings):
        """Test _stream_claude retries on initial connection failure."""
        from app.agents.base import BaseAgent
        from app.utils.retry import RetryConfig

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        call_count = 0

        mock_block1 = MagicMock(spec=TextBlock)
        mock_block1.text = "First "
        mock_block2 = MagicMock(spec=TextBlock)
        mock_block2.text = "chunk!"

        mock_assistant1 = MagicMock(spec=AssistantMessage)
        mock_assistant1.content = [mock_block1]
        mock_assistant2 = MagicMock(spec=AssistantMessage)
        mock_assistant2.content = [mock_block2]

        async def mock_query_fails_initially(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise TimeoutError("Initial timeout")
            yield mock_assistant1
            yield mock_assistant2

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query_fails_initially),
        ):
            agent = TestAgent(
                name="test-agent",
                retry_config=RetryConfig(
                    max_attempts=3,
                    base_delay=0.01,
                    jitter=False,
                ),
            )

            chunks = []
            async for chunk in agent._stream_claude("Stream test"):
                chunks.append(chunk)

            assert chunks == ["First ", "chunk!"]
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_start_conversation_retries_on_connection_error(
        self, mock_settings, mock_sdk_client
    ):
        """Test _start_conversation retries on connection failure."""
        from app.agents.base import BaseAgent
        from app.utils.retry import RetryConfig

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        call_count = 0

        async def mock_connect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise OSError("Connection refused")
            return None

        mock_sdk_client.connect = mock_connect

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.ClaudeSDKClient", return_value=mock_sdk_client),
        ):
            agent = TestAgent(
                name="test-agent",
                retry_config=RetryConfig(
                    max_attempts=3,
                    base_delay=0.01,
                    jitter=False,
                ),
            )

            await agent._start_conversation()

            assert agent._client is not None
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_config_from_settings(self, mock_settings):
        """Test BaseAgent uses retry config from settings when not provided."""
        from app.agents.base import BaseAgent

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        with patch("app.agents.base.settings", mock_settings):
            mock_settings.retry_max_attempts = 5
            mock_settings.retry_base_delay = 2.0
            mock_settings.retry_max_delay = 60.0
            mock_settings.retry_exponential_base = 3.0

            agent = TestAgent(name="test-agent")

            assert agent.retry_config.max_attempts == 5
            assert agent.retry_config.base_delay == 2.0
            assert agent.retry_config.max_delay == 60.0
            assert agent.retry_config.exponential_base == 3.0

    @pytest.mark.asyncio
    async def test_retry_config_override(self, mock_settings):
        """Test BaseAgent uses provided retry config over settings."""
        from app.agents.base import BaseAgent
        from app.utils.retry import RetryConfig

        class TestAgent(BaseAgent):
            async def run(self, *args, **kwargs):
                return None

        with patch("app.agents.base.settings", mock_settings):
            mock_settings.retry_max_attempts = 5
            mock_settings.retry_base_delay = 2.0

            custom_config = RetryConfig(max_attempts=10, base_delay=0.5)
            agent = TestAgent(name="test-agent", retry_config=custom_config)

            assert agent.retry_config.max_attempts == 10
            assert agent.retry_config.base_delay == 0.5


class TestQuickQueryRetry:
    """Tests for retry behavior in quick_query function."""

    @pytest.mark.asyncio
    async def test_quick_query_retries_on_connection_error(self, mock_settings):
        """Test quick_query retries on connection errors."""
        from app.utils.retry import RetryConfig

        call_count = 0

        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "Quick success!"

        mock_assistant = MagicMock(spec=AssistantMessage)
        mock_assistant.content = [mock_text_block]

        mock_result = MagicMock(spec=ResultMessage)
        mock_result.usage = {"input_tokens": 5, "output_tokens": 3}
        mock_result.duration_ms = 50
        mock_result.total_cost_usd = 0.0001
        mock_result.session_id = "quick-session"

        async def mock_query_fails_once(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Temporary failure")
            yield mock_assistant
            yield mock_result

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query_fails_once),
        ):
            from app.agents.base import quick_query

            result = await quick_query(
                "Quick test",
                retry_config=RetryConfig(max_attempts=3, base_delay=0.01, jitter=False),
            )

            assert result == "Quick success!"
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_quick_query_no_retry_on_query_error(self, mock_settings):
        """Test quick_query does NOT retry on application errors."""
        from app.agents.base import AgentQueryError
        from app.utils.retry import RetryConfig

        call_count = 0

        async def mock_query_raises_error(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise ValueError("Application error")
            yield

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query_raises_error),
        ):
            from app.agents.base import quick_query

            with pytest.raises(AgentQueryError, match="Quick query failed"):
                await quick_query(
                    "Quick test",
                    retry_config=RetryConfig(max_attempts=3, base_delay=0.01),
                )

            assert call_count == 1

    @pytest.mark.asyncio
    async def test_quick_query_exhausts_retries(self, mock_settings):
        """Test quick_query raises after exhausting all retry attempts."""
        from app.agents.base import AgentConnectionError
        from app.utils.retry import RetryConfig

        call_count = 0

        async def mock_query_always_fails(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Persistent connection failure")
            yield

        with (
            patch("app.agents.base.settings", mock_settings),
            patch("app.agents.base.query", mock_query_always_fails),
        ):
            from app.agents.base import quick_query

            with pytest.raises(AgentConnectionError, match="Failed to connect"):
                await quick_query(
                    "Quick test",
                    retry_config=RetryConfig(max_attempts=3, base_delay=0.01, jitter=False),
                )

            # Should have tried all 3 attempts
            assert call_count == 3
