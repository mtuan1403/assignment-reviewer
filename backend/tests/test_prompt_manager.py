from pathlib import Path
from backend.app.services.pipeline.prompt_manager import PromptManager


def test_prompt_manager_loads_system_prompt():
    pm = PromptManager()
    sys_prompt = pm.get_system_prompt()
    assert "senior university academic assessor" in sys_prompt
    assert "ZERO SYCOPHANCY" in sys_prompt


def test_prompt_manager_renders_evaluate_requirement():
    pm = PromptManager()
    rendered = pm.render_prompt(
        "evaluate_requirement",
        req_id="R1",
        req_category="deliverable",
        req_description="Provide a 4-page research proposal",
        mandatory=True,
        source_text="Must be 4 pages",
        source_page=2,
        context_str="Sample chunk text",
    )
    assert "Requirement ID: R1" in rendered
    assert "Provide a 4-page research proposal" in rendered
    assert "Sample chunk text" in rendered
    assert "OFF-TOPIC GATE" in rendered


def test_prompt_manager_renders_extract_requirements():
    pm = PromptManager()
    rendered = pm.render_prompt("extract_requirements", spec_text="Assessment task 1 details")
    assert "Assessment task 1 details" in rendered
    assert "Do not invent" in rendered or "Do NOT invent" in rendered
