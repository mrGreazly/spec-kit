"""Pi Coding Agent integration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..base import MarkdownIntegration
from ..manifest import IntegrationManifest


class PiIntegration(MarkdownIntegration):
    key = "pi"
    config = {
        "name": "Pi Coding Agent",
        "folder": ".pi/",
        "commands_subdir": "prompts",
        "install_url": "https://www.npmjs.com/package/@mariozechner/pi-coding-agent",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".pi/prompts",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": ".md",
        "strip_frontmatter_keys": ["handoffs"],
    }
    context_file = "AGENTS.md"

    def setup(
        self,
        project_root: Path,
        manifest: IntegrationManifest,
        parsed_options: dict[str, Any] | None = None,
        **opts: Any,
    ) -> list[Path]:
        """Install Pi prompts and strip unsupported handoff metadata.

        Pi prompt templates support standard frontmatter such as
        ``description`` and ``argument-hint``.  Spec Kit's ``handoffs``
        metadata is intended for agents with native handoff UI and is not
        consumed by Pi, so remove it from generated prompt templates.
        """
        created = super().setup(
            project_root, manifest, parsed_options=parsed_options, **opts
        )

        for path in created:
            if path.suffix != ".md":
                continue
            content = path.read_text(encoding="utf-8")
            updated = self._strip_handoffs_frontmatter(content)
            if updated != content:
                path.write_text(updated, encoding="utf-8")
                self.record_file_in_manifest(path, project_root, manifest)

        return created

    @staticmethod
    def _strip_handoffs_frontmatter(content: str) -> str:
        """Remove the top-level ``handoffs`` YAML frontmatter block."""
        lines = content.split("\n")
        if not lines or lines[0].strip() != "---":
            return content

        frontmatter_end = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                frontmatter_end = i
                break
        if frontmatter_end == -1:
            return content

        frontmatter_lines = lines[1:frontmatter_end]
        body_lines = lines[frontmatter_end + 1:]

        filtered_frontmatter: list[str] = []
        skip_until_outdent = False
        for line in frontmatter_lines:
            if skip_until_outdent:
                if line and (line[0] == " " or line[0] == "\t"):
                    continue
                skip_until_outdent = False

            if line.strip().startswith("handoffs:"):
                skip_until_outdent = True
                continue

            filtered_frontmatter.append(line)

        return "\n".join(["---", *filtered_frontmatter, "---", *body_lines])
