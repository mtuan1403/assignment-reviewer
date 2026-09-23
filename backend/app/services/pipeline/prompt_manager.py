import os
from pathlib import Path
from typing import Dict, Any, Optional
from backend.app.core.logging import get_logger

logger = get_logger(__name__)

# Default prompts directory: <project_root>/backend/prompts
DEFAULT_PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "prompts"


class PromptManager:
    """
    Loads and renders prompt templates from external .txt files in backend/prompts/.
    Enables developers to tweak prompts directly in text files without modifying Python code.
    Reads on demand so edits take effect immediately without restarting the application.
    """

    def __init__(self, prompts_dir: Optional[Path] = None):
        self.prompts_dir = prompts_dir or DEFAULT_PROMPTS_DIR
        logger.info(f"PromptManager initialized with prompts directory: {self.prompts_dir}")

    def _read_file(self, filename: str) -> str:
        filepath = self.prompts_dir / filename
        if not filepath.exists():
            logger.warning(f"Prompt file {filepath} not found. Attempting relative fallback.")
            # Fallback check
            alt_path = Path("backend/prompts") / filename
            if alt_path.exists():
                filepath = alt_path
            else:
                raise FileNotFoundError(f"Prompt file not found at {filepath} or {alt_path}")

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()

    def get_system_prompt(self) -> str:
        """Loads the global academic evaluator system prompt."""
        try:
            return self._read_file("system_prompt.txt")
        except Exception as e:
            logger.error(f"Failed to load system_prompt.txt: {e}")
            return (
                "You are a senior university academic assessor. "
                "Provide rigorous, evidence-grounded, objective evaluation of student submissions."
            )

    def render_prompt(self, template_name: str, **kwargs: Any) -> str:
        """
        Loads a prompt template .txt file and safely interpolates keyword arguments.
        Example: render_prompt("evaluate_requirement.txt", req_id="R1", ...)
        """
        filename = template_name if template_name.endswith(".txt") else f"{template_name}.txt"
        template_text = self._read_file(filename)

        try:
            return template_text.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing placeholder {e} while formatting {filename}. Proceeding with partial replacement.")
            # Fallback to replacement of provided keys
            result = template_text
            for k, v in kwargs.items():
                result = result.replace(f"{{{k}}}", str(v))
            return result


# Global singleton instance
prompt_manager = PromptManager()
