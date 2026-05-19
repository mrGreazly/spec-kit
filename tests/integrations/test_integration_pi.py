"""Tests for PiIntegration."""

from specify_cli.agents import CommandRegistrar
from specify_cli.integrations.manifest import IntegrationManifest
from specify_cli.integrations.pi import PiIntegration

from .test_integration_base_markdown import MarkdownIntegrationTests


class TestPiIntegration(MarkdownIntegrationTests):
    KEY = "pi"
    FOLDER = ".pi/"
    COMMANDS_SUBDIR = "prompts"
    REGISTRAR_DIR = ".pi/prompts"
    CONTEXT_FILE = "AGENTS.md"

    def test_handoffs_are_stripped_from_generated_prompts(self, tmp_path):
        """Pi prompt templates should not include unsupported handoff metadata."""
        pi = PiIntegration()
        manifest = IntegrationManifest("pi", tmp_path)
        pi.setup(tmp_path, manifest)

        registrar = CommandRegistrar()
        prompts_dir = tmp_path / ".pi" / "prompts"
        for prompt_file in prompts_dir.glob("speckit.*.md"):
            content = prompt_file.read_text(encoding="utf-8")
            frontmatter, _ = registrar.parse_frontmatter(content)
            assert "handoffs" not in frontmatter, (
                f"{prompt_file.name} has unstripped 'handoffs' key in frontmatter"
            )
