# AI-QE Studio

Agentic AI quality engineering prototype: orchestrated agents, knowledge bases, and generated test artifacts.

## Structure

```
AI-QE Studio
│
├── agents
│   ├── orchestrator.md
│   ├── requirement-analysis-agent.md
│   ├── test-generation-agent.md
│   └── validation-agent.md
│
├── knowledge
│   ├── customer-management-pack
│   │   ├── application-context.md
│   │   ├── business-rules.md
│   │   ├── data-model.md
│   │   ├── glossary.md
│   │   └── known-limitations.md
│   │
│   └── requirements
│       └── duplicate-customer-story.md
│
├── schemas
│   └── requirement-analysis-schema.md
│
├── examples
│   └── duplicate-customer-story
│       └── ... reference workflow artifacts
│
├── generated
├── orchestrator.py
├── ai_qe_studio/
└── README.md
```

## Agents

| Agent | Purpose |
| --- | --- |
| Orchestrator | Coordinates the QE agent workflow |
| Requirement Analysis | Analyzes requirements and extracts testable intent |
| Test Generation | Produces test artifacts from analyzed requirements |
| Validation | Validates generated tests against standards and knowledge |

## Knowledge

- **customer-management-pack** — Domain context, business rules, data model, glossary, and known limitations
- **requirements** — Source stories and requirement artifacts
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

## Run Requirement Analysis (Milestone 1)

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

## Run Test Generation (POC)

The current POC generates a **representative subset** of up to **10 tests** to prove the full pipeline:

```
Requirement → Requirement Analysis → Test Generation → Validation → Final verdict
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

Run unit tests with the standard library test runner:

```bash
python -m unittest discover -s tests -v
```
