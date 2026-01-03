"""
Prompt builder for Forge.

Generates rich, context-aware prompts for Claude Code implementation sessions
by combining project context, feature specifications, and expert perspectives.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re

from .registry import Feature, FeatureRegistry
from .intelligence import IntelligenceEngine, SuggestedExpert


@dataclass
class PromptContext:
    """Context gathered for prompt generation."""

    project_name: str
    claude_md_content: str
    feature: Feature
    spec_content: Optional[str] = None
    research_synthesis: Optional[str] = None
    expert_preamble: Optional[str] = None
    dependency_context: Optional[str] = None
    worktree_path: Optional[Path] = None
    project_context: Optional[str] = None  # From project-context.md
    refinement_context: Optional[str] = None  # Extracted from refine conversation


class PromptBuilder:
    """
    Builds implementation prompts for Claude Code.

    Combines:
    - Project CLAUDE.md for coding conventions
    - Feature specification
    - Expert perspectives (dynamically generated)
    - Research synthesis (if deep research was conducted)
    - Dependency context
    """

    def __init__(
        self,
        project_root: Path,
        registry: FeatureRegistry,
        intelligence: IntelligenceEngine,
    ):
        self.project_root = project_root
        self.registry = registry
        self.intelligence = intelligence

    def _read_claude_md(self, claude_md_path: str) -> str:
        """Read and extract relevant sections from CLAUDE.md."""
        full_path = self.project_root / claude_md_path

        if not full_path.exists():
            return ""  # No filler text - just skip section if no CLAUDE.md

        content = full_path.read_text()

        # Extract sections useful for implementation and DevOps hygiene
        # Prioritized: context that helps Claude implement correctly
        # Note: (?=\n## |\Z) stops at next H2 section, not H3 subsections
        sections_to_keep = [
            r"## Project Overview.*?(?=\n## |\Z)",
            r"## Terminology.*?(?=\n## |\Z)",          # Domain understanding
            r"## Architecture.*?(?=\n## |\Z)",
            r"## Coding Style.*?(?=\n## |\Z)",
            r"## Build Commands.*?(?=\n## |\Z)",
            r"## Testing.*?(?=\n## |\Z)",              # Code hygiene
            r"## Key Design Decisions.*?(?=\n## |\Z)", # Architectural context
            r"## Commit Conventions.*?(?=\n## |\Z)",   # DevOps hygiene
            r"## CLI Commands.*?(?=\n## |\Z)",         # Tool usage
            r"## Key Patterns.*?(?=\n## |\Z)",         # Implementation patterns
            r"## Common Patterns.*?(?=\n## |\Z)",      # Alternative naming
        ]

        extracted = []
        for pattern in sections_to_keep:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                extracted.append(match.group(0).strip())

        if extracted:
            return "\n\n".join(extracted)

        # If no sections matched, return trimmed version (first 5000 chars)
        # Increased from 3000 to give more context when sections don't match
        if len(content) > 5000:
            return content[:5000] + "\n\n... (truncated for brevity)"

        return content

    def _read_spec(self, spec_path: Optional[str]) -> Optional[str]:
        """Read feature specification file if it exists."""
        if not spec_path:
            return None

        full_path = self.project_root / spec_path

        if not full_path.exists():
            return None

        content = full_path.read_text()

        # Trim if too long
        if len(content) > 5000:
            return content[:5000] + "\n\n... (truncated for brevity)"

        return content

    def _build_dependency_context(self, feature: Feature) -> Optional[str]:
        """Build context about feature dependencies."""
        if not feature.depends_on:
            return None

        dep_info = []
        for dep_id in feature.depends_on:
            dep = self.registry.get_feature(dep_id)
            if dep:
                status = "✅ completed" if dep.status.value == "completed" else f"⚠️ {dep.status.value}"
                dep_info.append(f"- **{dep.title}** ({status}): {dep.description[:100]}")

        if not dep_info:
            return None

        return "## Dependencies\n\nThis feature depends on:\n" + "\n".join(dep_info)

    def _read_project_context(self) -> Optional[str]:
        """Read project context from .forge/project-context.md."""
        context_path = self.project_root / ".forge" / "project-context.md"
        if not context_path.exists():
            return None
        return context_path.read_text()

    def _extract_refinement_context(self, feature: Feature) -> Optional[str]:
        """
        Extract key context from refinement conversation using Opus.

        AGI-pilled approach: Pass the full conversation to Opus, let it decide
        what's important for the build agent. No brittle regex patterns.

        Uses Claude CLI with Max subscription (same as brainstorm agent).
        """
        import subprocess

        history = feature.extensions.get("refinement_history", [])
        if not history:
            return None

        # Format conversation for the summarization prompt
        conversation = []
        for msg in history:
            role = "User" if msg.get("role") == "user" else "Assistant"
            conversation.append(f"{role}: {msg.get('content', '')}")

        conversation_text = "\n\n".join(conversation)

        # Truncate if extremely long (>50K chars) - but include as much as possible
        # CONTEXT_LIMIT: May revisit as context windows expand
        if len(conversation_text) > 50000:
            conversation_text = conversation_text[:50000] + "\n\n[...conversation truncated...]"

        extraction_prompt = f"""You are preparing context for a build agent that will implement a feature.

The user refined this feature idea through a conversation. Extract the KEY context the build agent needs to know - things that might not be obvious from the final spec alone.

Focus on:
- **Non-requirements**: Things the user said NOT to do, to avoid, or explicitly rejected
- **References**: Products, patterns, or examples the user compared to ("like Notion's...", "similar to...")
- **Motivations**: WHY they want this (the underlying need, not just what)
- **Constraints**: Any limitations or requirements mentioned
- **Preferences**: UX preferences, behavior expectations, edge cases discussed

Do NOT include:
- Implementation details (the build agent has full codebase access)
- The final spec (that's passed separately)
- Generic conversation filler

If there's nothing notable beyond the spec, respond with just: "No additional context needed."

Keep it concise - bullet points, not paragraphs. The build agent is smart, just give it the signal.

---

REFINEMENT CONVERSATION:

{conversation_text}

---

CONTEXT FOR BUILD AGENT:"""

        try:
            # Use Claude CLI with Opus (Max subscription)
            result = subprocess.run(
                [
                    "claude",
                    "-p", extraction_prompt,
                    "--model", "opus",
                    "--output-format", "text",
                    "--allowedTools", "",  # No tools needed for summarization
                ],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
            )

            if result.returncode == 0 and result.stdout.strip():
                output = result.stdout.strip()
                # Check if Opus said no additional context needed
                if "no additional context" in output.lower():
                    return None
                return output

        except subprocess.TimeoutExpired:
            print("[PromptBuilder] Refinement context extraction timed out")
        except Exception as e:
            print(f"[PromptBuilder] Refinement context extraction failed: {e}")

        return None

    def gather_context(
        self,
        feature_id: str,
        claude_md_path: str = "CLAUDE.md",
        include_experts: bool = True,
        include_research: bool = True,
    ) -> PromptContext:
        """
        Gather all context needed for prompt generation.

        This is separated from build() to allow inspection before generation.
        """
        feature = self.registry.get_feature(feature_id)
        if not feature:
            raise ValueError(f"Feature not found: {feature_id}")

        # Read project context (from enhanced init)
        project_context = self._read_project_context()

        # Read CLAUDE.md
        claude_md_content = self._read_claude_md(claude_md_path)

        # Read feature spec
        spec_content = self._read_spec(feature.spec_path)

        # Load research synthesis if available
        research_synthesis = None
        if include_research:
            session = self.intelligence.load_session(feature_id)
            if session and session.synthesis:
                research_synthesis = session.synthesis

        # Generate expert preamble only if warranted (discretionary)
        expert_preamble = None
        if include_experts and not research_synthesis:
            # First check if this feature warrants expert consultation at all
            # Most features don't - only invoke for design challenges, architecture, domain expertise
            if self.intelligence.should_invoke_experts(
                feature.title,
                feature.description,
                feature.tags,
            ):
                experts = self.intelligence.suggest_experts(
                    feature.title,
                    feature.description,
                    feature.tags,
                )
                if experts:
                    expert_preamble = self.intelligence.generate_expert_preamble(experts)

        # Build dependency context
        dependency_context = self._build_dependency_context(feature)

        # Extract refinement context from conversation history
        refinement_context = self._extract_refinement_context(feature)

        return PromptContext(
            project_name=self.project_root.name,
            claude_md_content=claude_md_content,
            feature=feature,
            spec_content=spec_content,
            research_synthesis=research_synthesis,
            expert_preamble=expert_preamble,
            dependency_context=dependency_context,
            worktree_path=Path(feature.worktree_path) if feature.worktree_path else None,
            project_context=project_context,
            refinement_context=refinement_context,
        )

    def build(self, context: PromptContext) -> str:
        """
        Build the final implementation prompt from gathered context.

        Uses the AGI-pilled prompt template with:
        - Expert consultation patterns (Claude decides who)
        - Research guidance (Claude decides when)
        - Vibecoder context
        - Plan mode + ultrathink instructions
        """
        sections = []

        # Header
        sections.append(f"# Implement: {context.feature.title}")
        sections.append("")

        # Workflow context (situational awareness, not prescriptive)
        sections.append("## Workflow Context")
        sections.append("")
        sections.append("You're in a Forge-managed worktree for this feature.")
        sections.append(f"- **Feature ID:** `{context.feature.id}`")
        if context.worktree_path:
            sections.append(f"- **Worktree:** `{context.worktree_path}`")
        sections.append("- **Branch:** Isolated from main (changes won't affect main until shipped)")
        sections.append(f"- **To ship:** When human says \"ship it\", run `forge merge {context.feature.id}`")
        sections.append("- **Your focus:** Implement the feature. Human decides when to ship.")
        sections.append("")

        # Feature description
        sections.append("## Feature")
        sections.append(context.feature.description or "(No description provided)")
        sections.append("")

        if context.feature.tags:
            sections.append(f"**Tags:** {', '.join(context.feature.tags)}")
            sections.append("")

        # Research synthesis (highest priority context)
        if context.research_synthesis:
            sections.append("## Research & Design Context")
            sections.append(context.research_synthesis)
            sections.append("")

        # Expert perspectives (only included when dynamically generated - not boilerplate)
        if context.expert_preamble and not context.research_synthesis:
            sections.append(context.expert_preamble)
            sections.append("")

        # Research guidance - prompt USER to run research if needed (not prescriptive about where)
        if not context.research_synthesis:
            sections.append("## Research")
            sections.append("")
            sections.append("If this feature involves novel patterns, complex architecture, or unfamiliar APIs:")
            sections.append("- **Ask the human** to run deep research threads if you need authoritative context")
            sections.append("- For clinical/medical evidence, specifically ask them to check OpenEvidence")
            sections.append("- Cite official documentation where applicable")
            sections.append("")

        # Feature specification
        if context.spec_content:
            sections.append("## Specification")
            sections.append(context.spec_content)
            sections.append("")

        # Refinement context (extracted from refine conversation by Opus)
        if context.refinement_context:
            sections.append("## Context from Refinement")
            sections.append("*The following was extracted from the user's refinement conversation - things that may not be obvious from the spec:*")
            sections.append("")
            sections.append(context.refinement_context)
            sections.append("")

        # Dependencies
        if context.dependency_context:
            sections.append(context.dependency_context)
            sections.append("")

        # Project context (from enhanced init)
        if context.project_context:
            sections.append("## Project Vision")
            sections.append(context.project_context)
            sections.append("")

        # CLAUDE.md content (only if available)
        if context.claude_md_content:
            sections.append("## Project Context")
            sections.append(context.claude_md_content)
            sections.append("")

        # Implementation instructions (AGI-pilled)
        sections.append("## Instructions")
        sections.append("")
        sections.append("You're helping a vibecoder who isn't a Git expert.")
        sections.append("Handle all Git operations safely without requiring them to understand Git.")
        sections.append("")
        sections.append("**Engage plan mode and ultrathink before implementing.**")
        sections.append("Present your plan for approval before writing code.")
        sections.append("")
        sections.append("When implementing:")
        sections.append("- Commit changes with conventional commit format")
        sections.append("- Follow existing patterns in the codebase")
        sections.append("- Test on target device/environment")
        sections.append("")
        sections.append("When human says \"ship it\":")
        sections.append(f"- Run `forge ship` to merge to main and clean up")
        sections.append("- This handles: merge → build validation → worktree cleanup → celebrate!")
        sections.append("")
        sections.append("Ask clarifying questions if the specification is unclear.")
        sections.append("")

        return "\n".join(sections)

    def build_for_feature(
        self,
        feature_id: str,
        claude_md_path: str = "CLAUDE.md",
        include_experts: bool = True,
        include_research: bool = True,
    ) -> str:
        """
        Convenience method to gather context and build prompt in one call.
        """
        context = self.gather_context(
            feature_id,
            claude_md_path,
            include_experts,
            include_research,
        )
        return self.build(context)

    def save_prompt(self, feature_id: str, prompt: str) -> Path:
        """Save generated prompt to .forge/prompts/."""
        prompts_dir = self.project_root / ".forge" / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)

        prompt_path = prompts_dir / f"{feature_id}.md"
        prompt_path.write_text(prompt)

        return prompt_path
