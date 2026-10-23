# AI-QE Studio

Agentic AI quality engineering prototype: orchestrated agents, knowledge bases, and generated test artifacts.

## Status

| Stage | State | Output |
| --- | --- | --- |
| 1. Requirement Analysis | Built (`--stage requirement-analysis`, the default) | `generated/{story_name}/requirement-analysis.md` |
| 2. Test Generation | Built as a POC, up to 10 tests (`--stage test-generation`) | `generated/{story_name}/generated-test-suite.md` |
| 3. Validation | Not built. Agent contract only; the reports in `examples/` were produced outside this code | — |

Large-suite generation (batching, chunking, parallel runs, retries) is also not built yet.

## Structure

```
AI-QE Studio
│
├── orchestrator.py              CLI entry point (runs one stage per call)
├── ai_qe_studio/                Python package used by the orchestrator
│   ├── stages/
│   │   ├── requirement_analysis.py
│   │   └── test_generation.py
│   ├── anthropic_client.py      Anthropic API call and metadata logging
│   ├── config.py                .env and CLI settings
│   ├── paths.py                 Input/output file locations per stage
│   ├── prompts.py               Prompt assembly
│   ├── handoff.py               Reads and checks the Requirement Analysis handoff
│   ├── suite_validation.py      Checks a generated suite before it is written
│   ├── files.py
│   └── errors.py
│
├── agents/                      Agent contracts (instructions sent to the model)
│   ├── orchestrator.md
│   ├── requirement-analysis-agent.md
│   ├── test-generation-agent.md
│   └── validation-agent.md
│
├── knowledge/
│   ├── customer-management-pack/
│   │   ├── application-context.md
│   │   ├── business-rules.md
│   │   ├── data-model.md
│   │   ├── glossary.md
│   │   └── known-limitations.md
│   ├── qe-pack/
│   │   ├── gherkin-standards.md
│   │   ├── manual-testing.md
│   │   ├── severity-priority.md
│   │   └── test-design-techniques.md
│   └── requirements/
│       └── duplicate-customer-story.md
│
├── schemas/
│   └── requirement-analysis-schema.md
│
├── examples/duplicate-customer-story/   Reference artifacts, incl. validation reports v1–v3
├── generated/                   Stage outputs written by orchestrator.py
├── tests/                       Unit tests (unittest)
├── test_anthropic.py            Anthropic connection check
└── requirements.txt
```

## Agents

| Agent | Purpose | Used by the code |
| --- | --- | --- |
| Orchestrator | Describes the overall QE workflow | No. `orchestrator.py` implements the coordination directly |
| Requirement Analysis | Analyzes requirements and extracts testable intent | Yes, stage 1 |
| Test Generation | Produces test artifacts from analyzed requirements | Yes, stage 2 |
| Validation | Validates generated tests against standards and knowledge | Not yet |

## Knowledge

- **customer-management-pack** — Domain context, business rules, data model, glossary, and known limitations. Loaded by both built stages.
- **qe-pack** — QE standards (Gherkin, manual testing, severity/priority, test design techniques). Not loaded by the current stages.
- **requirements** — Source stories. The story slug passed to `orchestrator.py` must match a file here.
- **examples** — Reference end-to-end workflow outputs (read-only)

## Setup

1. Create and activate the virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-sonnet-5
ANTHROPIC_MAX_TOKENS=16384
ANTHROPIC_TIMEOUT_SECONDS=600
AI_QE_POC_MAX_TESTS=10
```

3. Verify the Anthropic connection:

```bash
python test_anthropic.py
```

## Run Requirement Analysis (Stage 1)

Run the orchestrator for a story slug that matches a file under `knowledge/requirements/`:

```bash
python orchestrator.py duplicate-customer-story
```

Optional flags:

```bash
python orchestrator.py duplicate-customer-story --requirement-id US-042
python orchestrator.py duplicate-customer-story --overwrite
python orchestrator.py duplicate-customer-story --max-tokens 4096
```

Behavior:

- Loads the requirement from `knowledge/requirements/{story_name}.md`
- Loads the Requirement Analysis agent contract, customer-management knowledge pack, and output schema
- Calls Anthropic using settings from `.env`
- Logs call metadata (model, token limits, prompt sizes, elapsed time) at INFO level — never logs the API key or prompt contents
- Writes output to `generated/{story_name}/requirement-analysis.md`
- Refuses to overwrite an existing output file unless `--overwrite` is passed

Use `--max-tokens` for faster first-run testing with a smaller output cap. Production runs should use the full `ANTHROPIC_MAX_TOKENS` value from `.env`.

## Run Test Generation (Stage 2, POC)

The current POC generates a **representative subset** of up to **10 tests**. The intended pipeline is below; the Validation step and final verdict are not built yet.

```
Requirement → Requirement Analysis → Test Generation → Validation (planned) → Final verdict (planned)
```

After Requirement Analysis has produced a ready handoff, run Test Generation:

```bash
python orchestrator.py duplicate-customer-story --stage test-generation
```

Optional flags:

```bash
python orchestrator.py duplicate-customer-story --stage test-generation --requirement-id US-042
python orchestrator.py duplicate-customer-story --stage test-generation --overwrite
python orchestrator.py duplicate-customer-story --stage test-generation --max-tokens 16384
python orchestrator.py duplicate-customer-story --stage test-generation --max-tests 10
```

POC configuration:

```env
AI_QE_POC_MAX_TESTS=10
```

Resolution order for the test limit: `--max-tests` → `AI_QE_POC_MAX_TESTS` → default `10`.

Behavior:

- Generates a **representative subset**, not an exhaustive suite
- Default maximum: **10 tests** including READY, CONSTRAINED, and BLOCKED cases
- Loads `generated/{story_name}/requirement-analysis.md` (must exist and be non-empty)
- Validates the Handoff Package in Python before calling Anthropic (`ready_for_test_generation: true`, schema 1.1 with 1.0 fallback)
- Uses the handoff `requirement_id` as the source of truth; if `--requirement-id` is supplied it must match the handoff
- Refuses to overwrite an existing output file unless `--overwrite` is passed (checked before the API call)
- Validates the model response **before writing**; validation failure **does not write or replace** `generated-test-suite.md`
- Loads the requirement, Test Generation agent contract, and customer-management knowledge pack only
- Includes the complete Requirement Analysis text in the prompt
- Writes output to `generated/{story_name}/generated-test-suite.md` only after validation passes

### Future: scale milestone (not implemented)

Exhaustive large-suite generation, batching, chunked generation, parallel runs, merge orchestration, and retry loops are **not implemented** in the current POC.

## Tests

Install `requirements.txt` first (the test-generation tests import `anthropic`), then run the unit tests with the standard library test runner:

```bash
python -m unittest discover -s tests -v
```
