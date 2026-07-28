"""Prompt assembly for orchestrator stages."""

from __future__ import annotations

from ai_qe_studio.paths import StoryPaths, TestGenerationPaths


def build_requirement_analysis_user_prompt(
    *,
    paths: StoryPaths,
    requirement_text: str,
    requirement_id: str,
    knowledge_contents: dict[str, str],
    schema_text: str,
) -> str:
    """Build the user message for the Requirement Analysis stage."""
    knowledge_sections = "\n\n".join(
        f"### {filename}\n\n{content}"
        for filename, content in knowledge_contents.items()
    )

    return (
        "Run the Requirement Analysis Agent for the input below.\n"
        "Follow the agent contract and produce the Markdown output "
        "defined in Section 9 of the agent specification.\n\n"
        "## Run Metadata\n\n"
        f"- requirement_id: {requirement_id}\n"
        f"- requirement_source: {paths.requirement_source}\n"
        f"- story_name: {paths.story_name}\n\n"
        "## Requirement\n\n"
        f"{requirement_text}\n\n"
        "## Knowledge Sources\n\n"
        f"{knowledge_sections}\n\n"
        "## Output Schema\n\n"
        f"{schema_text}\n"
    )


def build_test_generation_user_prompt(
    *,
    paths: TestGenerationPaths,
    requirement_text: str,
    requirement_id: str,
    analysis_text: str,
    knowledge_contents: dict[str, str],
    max_tests: int,
) -> str:
    """Build the user message for the Test Generation stage."""
    knowledge_sections = "\n\n".join(
        f"### knowledge/customer-management-pack/{filename}\n\n{content}"
        for filename, content in knowledge_contents.items()
    )
    loaded_knowledge_files = "\n".join(
        f"- knowledge/customer-management-pack/{filename}"
        for filename in knowledge_contents
    )

    return (
        "Run the Test Generation Agent for the input below.\n"
        "Follow the agent contract and produce the Markdown test suite "
        "defined in Section 9, ending with the Validation Handoff "
        "Package defined in Section 12.\n\n"
        "Use only the knowledge files listed under 'Loaded Knowledge Files'. "
        "Do not assume any other knowledge sources were provided.\n\n"
        "## POC Run Constraints\n\n"
        "- This is a **proof-of-concept** run intended to prove the routing "
        "model, not exhaustive coverage.\n"
        f"- Generate **no more than {max_tests}** test cases total "
        "(sequential TC-001 through TC-NNN only).\n"
        "- Produce a **representative subset**, not a full inventory.\n"
        "- Include **READY**, **CONSTRAINED**, and **BLOCKED** tests.\n"
        "- Target mix when the handoff supports it: approximately "
        "6 READY, 2 CONSTRAINED, and 2 BLOCKED; minimum 1 CONSTRAINED and "
        "1 BLOCKED are required.\n"
        "- Prioritize: core happy path, core negative path, permission or "
        "role behavior, lifecycle or audit behavior, one constrained "
        "scenario, one blocked scenario, and acceptance-criteria "
        "traceability.\n"
        "- The coverage map must list **only test IDs actually generated**.\n"
        "- Do **not** create a larger planned inventory than the written "
        "suite or reference phantom test IDs.\n"
        "- Document **intentionally deferred coverage** in the Validation "
        "Handoff Package instead of attempting exhaustive field, boundary, "
        "concurrency, or audit variation coverage.\n"
        f"- Set Validation Handoff Package fields poc_mode: true and "
        f"max_test_count: {max_tests} using the flat schema in Section 12.\n"
        "- Populate included_acceptance_criteria, deferred_coverage, and "
        "open_questions_referenced in the Validation Handoff Package.\n\n"
        "## POC Output Compactness\n\n"
        "- Do **not** repeat the complete Requirement Analysis in the output.\n"
        "- Do **not** include long narrative explanations between test cases.\n"
        "- Keep Assumptions and Open Questions sections concise.\n"
        "- Use only the test-case fields required by the agent contract.\n"
        "- Target a concise complete suite, not a lengthy report.\n"
        "- The coverage map and handoff must reference only generated tests.\n\n"
        "## Required Response Ending\n\n"
        "Your response is **invalid** unless it ends with the exact "
        "`## Validation Handoff Package` heading and a **closed** "
        "```yaml fenced block containing the flat handoff schema from "
        "Section 12.\n"
        "- The Validation Handoff Package must be the **final section**.\n"
        "- The fenced block must use `yaml` or `yml` and close with "
        "triple backticks.\n"
        "- Generate the handoff even when some tests are BLOCKED.\n\n"
        "## Validation Handoff Consistency (Strict)\n\n"
        "The Validation Handoff Package must be generated from the **final "
        "test cases actually written**. Test case bodies are the source of "
        "truth for downstream validation.\n\n"
        "Status rules for every generated test:\n"
        "- A test with numbered `### Expected Results` and no `[CONSTRAINED]` "
        "or `[BLOCKED]` title tag is **READY**.\n"
        "- A test titled `[CONSTRAINED]` or whose Expected Results begin with "
        "`CONSTRAINED —` is **CONSTRAINED**.\n"
        "- A test titled `[BLOCKED]` or whose Expected Results begin with "
        "`BLOCKED —` is **BLOCKED**.\n\n"
        "The Validation Handoff Package must match those bodies exactly:\n"
        "- Every `test_cases[].status` must equal the status implied by the "
        "final test body.\n"
        "- `ready_count`, `constrained_count`, and `blocked_count` must equal "
        "the tally from the final test bodies.\n"
        "- Do **not** infer status from open questions, deferred coverage, or "
        "Requirement Analysis routing alone.\n\n"
        "## Partial Open Question Routing\n\n"
        "When an acceptance criterion is fully testable, but an open question "
        "blocks only a narrower data-state, persistence, audit, or storage "
        "assertion:\n"
        "- Keep the behavioral test **READY**.\n"
        "- Exclude the unsupported data-state assertion from Expected Results.\n"
        "- Document the exclusion under Assumptions, Open Questions, or "
        "traceability notes.\n"
        "- Do **not** downgrade the entire test to CONSTRAINED or BLOCKED.\n"
        "- Use CONSTRAINED or BLOCKED only when the Expected Results "
        "themselves use that format.\n\n"
        "## Dismissal Workflow READY Pattern\n\n"
        "A supervisor dismissal workflow test may remain **READY** when the "
        "requirement clearly defines that:\n"
        "- an authorised supervisor can dismiss the flag,\n"
        "- a written reason is required,\n"
        "- the flag is cleared, and\n"
        "- the record becomes eligible for activation.\n\n"
        "An unresolved question about how the dismissal reason is stored or "
        "audited blocks only a separate persistence or audit data-state "
        "assertion — not the core behavioral dismissal test.\n\n"
        "## Final Self-Check Before Validation Handoff\n\n"
        "Before writing the Validation Handoff Package:\n"
        "1. Review every generated test case in final form.\n"
        "2. Determine each test's status from its title tag and Expected "
        "Results format.\n"
        "3. Recalculate `ready_count`, `constrained_count`, and "
        "`blocked_count` from those statuses.\n"
        "4. Populate `test_cases` and count fields only after this "
        "reconciliation.\n"
        "5. If any YAML status would disagree with a test body, revise the "
        "YAML to match the body before output.\n\n"
        "Honor the Requirement Analysis handoff routing:\n"
        "- Generate READY tests for fully testable scope.\n"
        "- Generate CONSTRAINED tests where partial coverage is achievable.\n"
        "- Generate BLOCKED tests where open questions with "
        "blocking_for_specific_tests: true prevent deterministic expected "
        "results.\n"
        "- Do not invent unresolved expected results.\n"
        "- Preserve open-question routing via affected_acceptance_criteria "
        "and affected_test_areas.\n\n"
        "## Run Metadata\n\n"
        f"- requirement_id: {requirement_id}\n"
        f"- requirement_source: {paths.requirement_source}\n"
        f"- story_name: {paths.story_name}\n"
        f"- max_test_count: {max_tests}\n"
        f"- poc_mode: true\n\n"
        "## Loaded Knowledge Files\n\n"
        f"{loaded_knowledge_files}\n\n"
        "## Original Requirement\n\n"
        f"{requirement_text}\n\n"
        "## Complete Requirement Analysis Output\n\n"
        f"{analysis_text}\n\n"
        "## Knowledge Sources\n\n"
        f"{knowledge_sections}\n"
    )
