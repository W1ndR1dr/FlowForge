"""
BrainstormAgent - Chat-to-spec conversations via Claude CLI.

This agent runs Claude Code CLI in streaming mode to enable real-time
brainstorming conversations. It's designed to run on the Pi and use the
user's authenticated Claude Max subscription.

Key CLI flags used:
- `--tools ""` - Chat-only mode, no file access
- `--output-format stream-json` - Real-time streaming
- `--append-system-prompt` - Add brainstorm instructions
- `--resume <session_id>` - Multi-turn conversations
"""

import asyncio
import json
import re
from dataclasses import dataclass, field
from typing import AsyncGenerator, Optional


@dataclass
class BrainstormMessage:
    """A message in the brainstorm conversation."""
    role: str  # "user" or "assistant"
    content: str


@dataclass
class SpecResult:
    """A crystallized spec from brainstorming."""
    title: str
    what_it_does: str
    how_it_works: list[str]
    files_affected: list[str]
    estimated_scope: str
    raw_spec: str

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "what_it_does": self.what_it_does,
            "how_it_works": self.how_it_works,
            "files_affected": self.files_affected,
            "estimated_scope": self.estimated_scope,
            "raw_spec": self.raw_spec,
        }


@dataclass
class BrainstormSession:
    """A brainstorming session with Claude."""
    project_name: str
    project_context: str
    existing_features: list[str]
    existing_feature_title: Optional[str] = None  # For crystallization mode
    messages: list[BrainstormMessage] = field(default_factory=list)
    spec_ready: bool = False
    current_spec: Optional[SpecResult] = None
    claude_session_id: Optional[str] = None  # Claude CLI session ID for --resume

    @property
    def is_crystallizing(self) -> bool:
        """Whether we're refining an existing feature vs brainstorming new ideas."""
        return self.existing_feature_title is not None

    def get_system_prompt(self) -> str:
        """Generate the system prompt for this session."""
        from .prompts import BRAINSTORM_SYSTEM_PROMPT, CRYSTALLIZE_SYSTEM_PROMPT

        features_str = "\n".join(f"- {f}" for f in self.existing_features) if self.existing_features else "(none yet)"

        if self.is_crystallizing:
            return CRYSTALLIZE_SYSTEM_PROMPT.format(
                project_name=self.project_name,
                project_context=self.project_context or "(no project context provided)",
                feature_title=self.existing_feature_title,
                existing_features=features_str,
            )
        else:
            return BRAINSTORM_SYSTEM_PROMPT.format(
                project_name=self.project_name,
                project_context=self.project_context or "(no project context provided)",
                existing_features=features_str,
            )


class BrainstormAgent:
    """
    Agent that facilitates brainstorming conversations via Claude CLI.

    Runs on the Pi, uses the user's Claude Max subscription.
    Streams responses back for real-time chat experience.

    Uses Claude CLI's native multi-turn support via --resume for efficient
    conversations without rebuilding the full prompt each time.
    """

    def __init__(
        self,
        project_name: str,
        project_context: str = "",
        existing_features: Optional[list[str]] = None,
        existing_feature_title: Optional[str] = None,
        existing_history: Optional[list[dict]] = None,
        claude_session_id: Optional[str] = None,  # Resume existing Claude session
    ):
        self.session = BrainstormSession(
            project_name=project_name,
            project_context=project_context,
            existing_features=existing_features or [],
            existing_feature_title=existing_feature_title,
            claude_session_id=claude_session_id,
        )

        # Load existing history if provided (for UI display)
        if existing_history:
            for msg in existing_history:
                self.session.messages.append(
                    BrainstormMessage(role=msg["role"], content=msg["content"])
                )

    async def send_message(
        self,
        user_message: str,
    ) -> AsyncGenerator[str, None]:
        """
        Send a message and stream the response.

        Yields chunks of the response as they come in.
        """
        # Add user message to history
        self.session.messages.append(BrainstormMessage(role="user", content=user_message))

        # Run claude CLI with streaming
        async for chunk in self._run_claude_streaming(user_message):
            yield chunk

        # After streaming complete, check if spec is ready
        if self.session.messages and self.session.messages[-1].role == "assistant":
            last_response = self.session.messages[-1].content
            if "SPEC_READY" in last_response:
                self.session.spec_ready = True
                self.session.current_spec = self._parse_spec(last_response)

    async def _run_claude_streaming(self, user_message: str) -> AsyncGenerator[str, None]:
        """
        Run Claude CLI and stream the response.

        Uses:
        - `--tools ""` for chat-only mode (no file access)
        - `--output-format stream-json` for real-time streaming
        - `--append-system-prompt` for brainstorm instructions
        - `--resume` for multi-turn conversations
        """
        cmd = [
            "claude",
            "-p", user_message,
            "--tools", "",  # Chat-only, no file access
            "--output-format", "stream-json",
        ]

        # First message: include system prompt
        # Subsequent messages: use --resume to continue conversation
        if self.session.claude_session_id:
            cmd.extend(["--resume", self.session.claude_session_id])
        else:
            # First message - include system prompt
            cmd.extend(["--append-system-prompt", self.session.get_system_prompt()])

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        full_response = []
        buffer = ""

        # Read and parse stream-json output
        while True:
            chunk = await process.stdout.read(1024)
            if not chunk:
                break

            buffer += chunk.decode("utf-8", errors="replace")

            # Process complete JSON lines
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)

                    # Extract session ID from first response
                    if not self.session.claude_session_id and "session_id" in data:
                        self.session.claude_session_id = data["session_id"]

                    # Handle different message types
                    msg_type = data.get("type")

                    if msg_type == "assistant":
                        # Assistant message content
                        content = data.get("message", {}).get("content", [])
                        for block in content:
                            if block.get("type") == "text":
                                text = block.get("text", "")
                                full_response.append(text)
                                yield text

                    elif msg_type == "content_block_delta":
                        # Streaming delta
                        delta = data.get("delta", {})
                        if delta.get("type") == "text_delta":
                            text = delta.get("text", "")
                            full_response.append(text)
                            yield text

                    elif msg_type == "result":
                        # Final result - extract session_id if not already captured
                        if not self.session.claude_session_id:
                            self.session.claude_session_id = data.get("session_id")
                        # Result text
                        result_text = data.get("result", "")
                        if result_text and not full_response:
                            full_response.append(result_text)
                            yield result_text

                except json.JSONDecodeError:
                    # Not valid JSON, might be partial - skip
                    pass

        # Wait for process to complete
        await process.wait()

        # Check stderr for errors
        stderr = await process.stderr.read()
        if stderr and process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace")
            # Log but don't fail - some warnings are benign
            print(f"Claude CLI stderr: {error_msg}")

        # Store the full response
        response_text = "".join(full_response)
        if response_text:
            self.session.messages.append(BrainstormMessage(role="assistant", content=response_text))

    def _parse_spec(self, response: str) -> Optional[SpecResult]:
        """Parse a SPEC_READY response into a SpecResult."""
        try:
            spec_match = re.search(r"SPEC_READY\s*\n(.*)", response, re.DOTALL)
            if not spec_match:
                return None

            spec_text = spec_match.group(1).strip()

            title = ""
            title_match = re.search(r"FEATURE:\s*(.+?)(?:\n|$)", spec_text)
            if title_match:
                title = title_match.group(1).strip()

            what_it_does = ""
            what_match = re.search(r"WHAT IT DOES:\s*\n(.+?)(?=\n\n|\nHOW IT WORKS:)", spec_text, re.DOTALL)
            if what_match:
                what_it_does = what_match.group(1).strip()

            how_it_works = []
            how_match = re.search(r"HOW IT WORKS:\s*\n(.+?)(?=\n\n|\nFILES|$)", spec_text, re.DOTALL)
            if how_match:
                how_text = how_match.group(1)
                how_it_works = [line.strip().lstrip("- ") for line in how_text.split("\n") if line.strip()]

            files_affected = []
            files_match = re.search(r"FILES LIKELY AFFECTED:\s*\n(.+?)(?=\n\n|\nESTIMATED|$)", spec_text, re.DOTALL)
            if files_match:
                files_text = files_match.group(1)
                files_affected = [line.strip().lstrip("- ") for line in files_text.split("\n") if line.strip()]

            estimated_scope = "Medium"
            scope_match = re.search(r"ESTIMATED SCOPE:\s*(.+?)(?:\n|$)", spec_text)
            if scope_match:
                estimated_scope = scope_match.group(1).strip()

            return SpecResult(
                title=title,
                what_it_does=what_it_does,
                how_it_works=how_it_works,
                files_affected=files_affected,
                estimated_scope=estimated_scope,
                raw_spec=spec_text,
            )
        except Exception:
            return None

    def get_conversation_state(self) -> dict:
        """Get the current state of the conversation."""
        return {
            "project_name": self.session.project_name,
            "message_count": len(self.session.messages),
            "spec_ready": self.session.spec_ready,
            "current_spec": self.session.current_spec.to_dict() if self.session.current_spec else None,
            "claude_session_id": self.session.claude_session_id,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in self.session.messages
            ],
        }

    def is_spec_ready(self) -> bool:
        """Check if a spec has crystallized from the conversation."""
        return self.session.spec_ready

    def get_spec(self) -> Optional[SpecResult]:
        """Get the crystallized spec, if ready."""
        return self.session.current_spec


async def test_brainstorm():
    """Quick test of the brainstorm agent."""
    agent = BrainstormAgent(
        project_name="TestApp",
        project_context="A simple todo app",
        existing_features=["Add tasks", "Mark complete"],
    )

    print("Testing brainstorm agent...")
    print("=" * 50)
    async for chunk in agent.send_message("I want to add due dates to tasks"):
        print(chunk, end="", flush=True)
    print("\n" + "=" * 50)
    print(f"Session ID: {agent.session.claude_session_id}")
    print(f"Spec ready: {agent.is_spec_ready()}")


if __name__ == "__main__":
    asyncio.run(test_brainstorm())
