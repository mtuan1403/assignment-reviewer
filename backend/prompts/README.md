# AI Reviewer Prompt Templates

This directory contains the editable prompt templates used across all stages of the AI Assignment Reviewer pipeline.

You can modify any of these text files directly. The system reads them on-the-fly, so **any changes you save will take effect immediately on your next review run without needing to restart the backend server**.

---

## Files & Placeholders

### 1. `system_prompt.txt`
- **Role**: Global system instructions defining the AI evaluator persona, tone, strictness, and anti-hallucination rules.
- **Used in**: All LLM calls (Gemini, Ollama, OpenAI).
- **Available Placeholders**: None (static text).

### 2. `extract_requirements.txt`
- **Role**: Stage 2 — Extracting structured requirements from the assignment specification PDF/DOCX.
- **Available Placeholders**:
  - `{spec_text}`: Extracted page & section text from the assignment specification.

### 3. `extract_rubric.txt`
- **Role**: Stage 3 — Extracting criteria, weightings, and performance level descriptors from the rubric.
- **Available Placeholders**:
  - `{rubric_text}`: Extracted text from the rubric document or specification marking section.

### 4. `evaluate_requirement.txt`
- **Role**: Stage 5 — Evaluating a single requirement against retrieved semantic chunks of the student submission.
- **Available Placeholders**:
  - `{req_id}`: The requirement identifier (e.g. `R1`).
  - `{req_category}`: Category (`explicit`, `deliverable`, `assessment`, `formatting`).
  - `{req_description}`: The text description of the requirement.
  - `{mandatory}`: `True` or `False`.
  - `{source_text}`: The exact excerpt from the spec where this requirement was found.
  - `{source_page}`: The page number in the spec.
  - `{context_str}`: The top retrieved chunks of student work with page numbers and chunk IDs.

### 5. `evaluate_rubric.txt`
- **Role**: Stage 6 — Estimating performance grade tier (HD, D, CR, P, Fail) for a rubric criterion.
- **Available Placeholders**:
  - `{crit_id}`: The criterion identifier (e.g. `C1`).
  - `{crit_name}`: Criterion name (e.g. `Critical Literature Review`).
  - `{weight}`: Percentage weight (e.g. `20`).
  - `{levels_str}`: Formatted list of grade bands and descriptors.
  - `{context_str}`: The top retrieved chunks of student work.

---

## Tips for Prompt Engineering

1. **Strictness vs. Leniency**:
   - If the AI is giving scores that are too high on weak drafts, emphasize in `system_prompt.txt` and `evaluate_requirement.txt` that "passing requires explicit analytical justification, not just mentioning keywords".
2. **Off-Topic Detection**:
   - The prompts include strict "OFF-TOPIC GATES" instructing the model to assign `MISSING` / `Fail` with confidence `1.0` if the text deviates from the assignment brief.
3. **Evidence Citations**:
   - Always keep the rule that quotes must be exact substrings from the `{context_str}` to prevent hallucinations.
