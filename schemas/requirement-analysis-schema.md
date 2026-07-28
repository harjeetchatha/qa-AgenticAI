# Requirement Analysis Schema

**Schema Name:** Requirement Analysis Object
**Schema ID:** `AIQE-SCHEMA-001`
**Version:** 1.1
**Status:** Active
**Owner:** AI-QE Studio

> **Purpose of This Document:** This document defines the enterprise data contract for the Requirement Analysis Object — the structured output produced by the Requirement Analysis Agent at the end of every analysis run. Every implementation of the Requirement Analysis Agent, regardless of the technology or orchestration framework used, must produce an object that satisfies this schema. This is a semantic contract, not a serialisation format. Implementations may serialise the object as YAML, JSON, or any other format, but the field names, types, validation rules, and relationships defined here are canonical and binding.

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Schema Versioning](#2-schema-versioning)
3. [Required Fields](#3-required-fields)
4. [Optional Fields](#4-optional-fields)
5. [Field Definitions](#5-field-definitions)
6. [Validation Rules](#6-validation-rules)
7. [Required Relationships](#7-required-relationships)
8. [Example Object](#8-example-object)
9. [Backward Compatibility Rules](#9-backward-compatibility-rules)

---

## 1. Purpose

The Requirement Analysis Object is the single structured artifact that the Requirement Analysis Agent produces after analysing a requirement against the AI-QE Studio knowledge base. It serves three purposes:

1. **Gate artifact** — The Orchestrator reads `ready_for_test_generation` to decide whether the workflow may proceed to the Test Generation Agent.
2. **Input contract** — The Test Generation Agent reads this object as its primary input. Every field the Test Generation Agent depends on must be present and valid before it is invoked.
3. **Audit record** — The object is stored as part of the Workflow Record and must be readable by the Validation Agent and by human reviewers to understand the analytical basis for every generated test case.

An object that satisfies this schema is a complete, self-contained representation of the analysis for a single requirement. It must not depend on external state that is not captured within the object itself.

---

## 2. Schema Versioning

| Field | Value |
|---|---|
| Schema ID | `AIQE-SCHEMA-001` |
| Current Version | `1.1` |
| Introduced | 2026-07-24 |
| Minimum Compatible Consumer Version | `1.0` |

**Version 1.1 changes (minor):**
- Added `blocking_for_specific_tests` and `blocking_for_entire_suite` on Question objects.
- Added optional `readiness` structured object with `suite_blockers` and `expected_generation_mix`.
- Relaxed suite-level `ready_for_test_generation` gate — unresolved test-level questions no longer block the suite by default.
- Deprecated `blocking` and `affects_ready` on Question objects (consumers must map per Section 9).

**Version field:** Every Requirement Analysis Object must carry a `schema_version` field set to the version of this schema it was produced against. This allows consumers to validate compatibility before reading the object.

**Version format:** `{major}.{minor}` — integer major version, integer minor version, dot-separated.

**Breaking vs. non-breaking changes:**
- A major version increment signals a breaking change: a field has been removed, renamed, or its allowed values have changed incompatibly.
- A minor version increment signals a non-breaking addition: a new optional field has been added.

See Section 9 for full backward compatibility rules.

---

## 3. Required Fields

The following fields must be present in every valid Requirement Analysis Object. An object missing any required field is invalid and must be rejected by any consumer.

| # | Field Name | Type |
|---|---|---|
| 1 | `schema_version` | String |
| 2 | `requirement_id` | String |
| 3 | `requirement_summary` | String |
| 4 | `business_objective` | String |
| 5 | `actors` | Array of Actor objects |
| 6 | `impacted_features` | Array of strings |
| 7 | `impacted_business_rules` | Array of Business Rule Reference objects |
| 8 | `impacted_entities` | Array of Entity Reference objects |
| 9 | `impacted_fields` | Array of Field Reference objects |
| 10 | `relevant_limitations` | Array of Limitation Reference objects |
| 11 | `acceptance_criteria_status` | Array of Acceptance Criterion Status objects |
| 12 | `ambiguities` | Array of Ambiguity objects |
| 13 | `unresolved_questions` | Array of Question objects |
| 14 | `assumptions` | Array of Assumption objects |
| 15 | `recommended_test_areas` | Array of Test Area objects |
| 16 | `risk_level` | Enum string |
| 17 | `risk_reason` | String |
| 18 | `confidence` | Enum string |
| 19 | `ready_for_test_generation` | Boolean |

---

## 4. Optional Fields

The following fields may be absent without invalidating the object. Consumers must not fail if these fields are absent; they must treat absence as equivalent to a null or empty value.

| Field Name | Type | Default when Absent |
|---|---|---|
| `schema_version` note — while listed as required above, consumers at minor-version mismatch must treat this field as advisory | — | — |
| `requirement_source` | String | `null` |
| `analysis_date` | Date string (YYYY-MM-DD) | `null` |
| `domain_context` | String | `"Customer Management Portal"` |
| `conflicts` | Array of Conflict objects | Empty array |
| `readiness` | Readiness object | See Section 5.21 — `suite_blockers` defaults to empty array; `expected_generation_mix` may be absent |
| `blocker_reason` | String | `null` — must be present when `ready_for_test_generation` is `false` |

> **Note on `blocker_reason`:** Although listed as optional in the field type sense, it is **conditionally required**: if `ready_for_test_generation` is `false`, `blocker_reason` must be present and non-empty. See Validation Rule VR-012.

---

## 5. Field Definitions

---

### 5.1 `schema_version`

| Attribute | Value |
|---|---|
| **Description** | The version of this schema the object was produced against. Used by consumers to validate compatibility. |
| **Required** | Yes |
| **Type** | String |
| **Allowed Values** | A valid version string of the form `{major}.{minor}` where both parts are non-negative integers (e.g., `"1.0"`, `"1.2"`, `"2.0"`). |
| **Validation Rules** | Must match the pattern `^\d+\.\d+$`. Must not be empty. |
| **Example** | `"1.0"` |

---

### 5.2 `requirement_id`

| Attribute | Value |
|---|---|
| **Description** | The unique identifier of the requirement that was analysed. This value is the primary key linking this object to the Workflow Record, the test suite, and the validation report. It must be passed through unchanged to all downstream agents. |
| **Required** | Yes |
| **Type** | String |
| **Allowed Values** | Any non-empty string. Recommended format: alphanumeric with hyphens (e.g., `US-042`, `CR-007`, `FEAT-112`). |
| **Validation Rules** | Must not be empty. Must not contain whitespace-only characters. Must match the `requirement_id` in the Workflow Record that triggered this analysis run. |
| **Example** | `"US-042"` |

---

### 5.3 `requirement_summary`

| Attribute | Value |
|---|---|
| **Description** | A concise, plain-English summary of what the requirement asks the system to do. Written by the Requirement Analysis Agent in Step 1 of its analysis process. Must not restate the requirement verbatim — it must convey the agent's understanding of the requirement's intent. |
| **Required** | Yes |
| **Type** | String |
| **Allowed Values** | Any non-empty string. Minimum 20 words. Maximum 200 words. |
| **Validation Rules** | Must not be empty. Must not be whitespace-only. Word count must be between 20 and 200 inclusive. Must not contain placeholder text (e.g., `{summary}`, `TBD`, `TODO`). |
| **Example** | `"When a user with Agent role attempts to create a new customer record, the system must run duplicate detection before activating the record. If a potential duplicate is found, the record must be flagged and the Agent must not be able to activate it without Supervisor approval."` |

---

### 5.4 `business_objective`

| Attribute | Value |
|---|---|
| **Description** | A single sentence identifying the underlying business goal the requirement serves. Must reference one of the business objectives defined in `application-context.md` Section 11 where applicable. Must not restate the requirement summary. |
| **Required** | Yes |
| **Type** | String |
| **Allowed Values** | Any non-empty string. Maximum 100 words. Must be a single sentence. |
| **Validation Rules** | Must not be empty. Must not be whitespace-only. Must not contain placeholder text. |
| **Example** | `"Prevent duplicate Active customer records from entering the system by gating activation on duplicate detection and Supervisor approval."` |

---

### 5.5 `actors`

| Attribute | Value |
|---|---|
| **Description** | All actors (users or systems) mentioned or implied by the requirement, each mapped to a defined role. |
| **Required** | Yes |
| **Type** | Array of Actor objects. Must contain at least one entry. |
| **Allowed Values** | Each Actor object must have: `actor` (string, the name used in the requirement), `role` (enum), `source` (string citation). |
| **`role` Allowed Values** | `"Viewer"`, `"Agent"`, `"Supervisor"`, `"Administrator"`, `"System"`, `"UNMAPPED"` |
| **Validation Rules** | Array must not be empty. Every entry must have a non-empty `actor` and a non-empty `role`. `"UNMAPPED"` is only permitted when the actor cannot be matched to a defined role; in that case `source` must contain an explanation of why mapping failed. |
| **Example** | `[{ "actor": "Customer Service Representative", "role": "Agent", "source": "glossary.md — Agent Role" }, { "actor": "Team Lead", "role": "Supervisor", "source": "application-context.md Section 3" }]` |

---

### 5.6 `impacted_features`

| Attribute | Value |
|---|---|
| **Description** | The named features from `application-context.md` Section 5 (Core Features) that this requirement touches. Used by the Test Generation Agent to scope its knowledge retrieval. |
| **Required** | Yes |
| **Type** | Array of strings. May be empty if no specific feature mapping is possible, but the analysis must explain why in `ambiguities`. |
| **Allowed Values** | Each string must match a feature name as it appears in `application-context.md` Section 5. |
| **Validation Rules** | Each value must be a non-empty string. Duplicate values within the array are not permitted. |
| **Example** | `["Customer record management", "Duplicate detection", "Account status management"]` |

---

### 5.7 `impacted_business_rules`

| Attribute | Value |
|---|---|
| **Description** | All business rules from `business-rules.md` that this requirement exercises, is constrained by, or conflicts with. The Test Generation Agent uses this list to determine which rules must have test coverage. |
| **Required** | Yes |
| **Type** | Array of Business Rule Reference objects. May be empty only if no business rules are relevant; this itself is a flag for human review. |

**Business Rule Reference Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `id` | String | Yes | The business rule ID exactly as it appears in `business-rules.md` (e.g., `"BR-004"`). |
| `title` | String | Yes | The rule title exactly as it appears in `business-rules.md`. |
| `relevance` | String | Yes | One sentence explaining why this rule is relevant to the requirement. |
| `relationship` | Enum | Yes | `"Exercised"`, `"Constrained by"`, or `"Conflicted"`. |

| Attribute | Value |
|---|---|
| **Validation Rules** | Every `id` must exist in `business-rules.md`. IDs that do not exist in the knowledge base are invalid. The `relationship` field must be one of the three allowed values. Duplicate `id` values within the array are not permitted. |
| **Example** | `[{ "id": "BR-004", "title": "Duplicate Check Before Activation", "relevance": "The requirement requires duplicate detection to run before a new record can be activated.", "relationship": "Exercised" }, { "id": "BR-015", "title": "Duplicate Flag Blocks Activation", "relevance": "The duplicate flag must block Pending → Active transition until resolved.", "relationship": "Exercised" }]` |

---

### 5.8 `impacted_entities`

| Attribute | Value |
|---|---|
| **Description** | All data model entities from `data-model.md` that this requirement reads, creates, updates, or transitions. |
| **Required** | Yes |
| **Type** | Array of Entity Reference objects. Must contain at least one entry if any data operation is involved. |

**Entity Reference Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `entity` | String | Yes | The entity name exactly as it appears in `data-model.md` (e.g., `"Customer"`, `"Email"`). |
| `operations` | Array of enum strings | Yes | One or more of: `"Create"`, `"Read"`, `"Update"`, `"Validate"`, `"Transition"`. |
| `source` | String | Yes | Citation — e.g., `"data-model.md Section 1"`. |

| Attribute | Value |
|---|---|
| **Validation Rules** | Every `entity` must exist in `data-model.md`. `operations` must contain at least one value. Duplicate `entity` values within the array are not permitted — if multiple operations apply to the same entity, list them all in a single entry's `operations` array. |
| **Example** | `[{ "entity": "Customer", "operations": ["Create", "Validate", "Transition"], "source": "data-model.md Section 1" }, { "entity": "Email", "operations": ["Validate"], "source": "data-model.md Section 3" }]` |

---

### 5.9 `impacted_fields`

| Attribute | Value |
|---|---|
| **Description** | All specific fields from `data-model.md` that this requirement reads, writes, or validates. Provides the Test Generation Agent with the precise data points that need test data and boundary analysis. |
| **Required** | Yes |
| **Type** | Array of Field Reference objects. |

**Field Reference Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `entity` | String | Yes | The parent entity name, must match a value in `impacted_entities`. |
| `field` | String | Yes | The field name exactly as it appears in `data-model.md`. |
| `operation` | Enum string | Yes | One of: `"Create"`, `"Read"`, `"Update"`, `"Validate"`. |
| `constraint` | String | No | The relevant validation rule or boundary condition from `data-model.md`, if one applies. |
| `sensitive` | Boolean | No | `true` if the field carries a sensitivity classification in `data-model.md`; `false` or absent otherwise. |

| Attribute | Value |
|---|---|
| **Validation Rules** | Every `entity` must match an entry in `impacted_entities`. Every `field` must exist on its parent entity in `data-model.md`. `operation` must be one of the four allowed values. Duplicate `entity` + `field` + `operation` combinations are not permitted. |
| **Example** | `[{ "entity": "Customer", "field": "status", "operation": "Validate", "constraint": "Must follow permitted transition matrix per BR-016", "sensitive": false }, { "entity": "Email", "field": "email_address", "operation": "Validate", "constraint": "RFC 5321 format; max 254 chars; unique across Active and Pending primary emails", "sensitive": true }]` |

---

### 5.10 `relevant_limitations`

| Attribute | Value |
|---|---|
| **Description** | All known limitations from `known-limitations.md` that constrain the requirement, bound its testing scope, or exclude specific behaviours from test coverage. |
| **Required** | Yes |
| **Type** | Array of Limitation Reference objects. May be empty if no limitations apply. |

**Limitation Reference Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `id` | String | Yes | The limitation ID exactly as it appears in `known-limitations.md` (e.g., `"LIM-004"`). |
| `title` | String | Yes | The limitation title exactly as it appears in `known-limitations.md`. |
| `impact` | String | Yes | One sentence explaining how the limitation constrains the requirement or its testing. |

| Attribute | Value |
|---|---|
| **Validation Rules** | Every `id` must exist in `known-limitations.md`. IDs that do not exist in the knowledge base are invalid. Duplicate `id` values within the array are not permitted. |
| **Example** | `[{ "id": "LIM-004", "title": "No Bulk Customer Creation", "impact": "Test scenarios must use individual record creation calls; bulk creation scenarios are out of scope." }]` |

---

### 5.11 `acceptance_criteria_status`

| Attribute | Value |
|---|---|
| **Description** | The assessment of every acceptance criterion stated in the requirement. Each criterion is classified for testability and any missing information is documented. |
| **Required** | Yes |
| **Type** | Array of Acceptance Criterion Status objects. If the requirement has no acceptance criteria, this array contains one entry with `id: "AC-0"` and `classification: "Not Testable"` and `missing_information` explaining that no AC were provided. |

**Acceptance Criterion Status Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `id` | String | Yes | Sequential identifier: `"AC-1"`, `"AC-2"`, etc. `"AC-0"` reserved for the no-criteria case. |
| `text` | String | Yes | The verbatim text of the acceptance criterion from the requirement. |
| `classification` | Enum string | Yes | `"Testable"`, `"Partially Testable"`, or `"Not Testable"`. |
| `missing_information` | String | No | Required when `classification` is `"Partially Testable"` or `"Not Testable"`. Describes specifically what information is absent. |

| Attribute | Value |
|---|---|
| **Validation Rules** | `id` values must be unique within the array. `classification` must be one of the three allowed values. `missing_information` must be present and non-empty when `classification` is `"Partially Testable"` or `"Not Testable"`. |
| **Example** | `[{ "id": "AC-1", "text": "Given a new customer record with a matching email to an Active record, when the Agent attempts to activate it, then a duplicate flag must be raised.", "classification": "Testable", "missing_information": null }, { "id": "AC-2", "text": "The system should handle edge cases appropriately.", "classification": "Not Testable", "missing_information": "No specific edge cases are named. 'Appropriately' has no testable definition." }]` |

---

### 5.12 `ambiguities`

| Attribute | Value |
|---|---|
| **Description** | A list of specific, answerable ambiguities detected in the requirement — vague terms, unstated conditions, missing negative behaviours, or actors with unspecified permissions. |
| **Required** | Yes |
| **Type** | Array of Ambiguity objects. May be empty if no ambiguities are found. |

**Ambiguity Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `id` | String | Yes | Sequential identifier: `"AMB-1"`, `"AMB-2"`, etc. |
| `description` | String | Yes | A specific, answerable question or statement of what is ambiguous. Must not be a general observation. |
| `affected_criteria` | Array of strings | No | The AC-IDs affected by this ambiguity, if any. |

| Attribute | Value |
|---|---|
| **Validation Rules** | `id` values must be unique within the array. `description` must not be empty or a general observation — it must be specific and answerable. |
| **Example** | `[{ "id": "AMB-1", "description": "The requirement states the Agent 'notifies' the Supervisor when a duplicate flag is raised, but does not define the notification mechanism or channel. Is this an in-portal alert, an email, or a system event?", "affected_criteria": ["AC-1"] }]` |

---

### 5.13 `unresolved_questions`

| Attribute | Value |
|---|---|
| **Description** | A numbered list of specific questions for the Product Owner or human reviewer. Questions may block specific tests, the entire suite, or neither. Test-level blockers route to CONSTRAINED or BLOCKED tests; suite-level blockers gate `ready_for_test_generation`. |
| **Required** | Yes |
| **Type** | Array of Question objects. May be empty if no questions remain. |

**Question Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `id` | String | Yes | Sequential identifier: `"Q-1"`, `"Q-2"`, etc. |
| `question` | String | Yes | The specific, answerable question for the Product Owner. |
| `blocking_for_specific_tests` | Boolean | Yes (1.1+) | `true` if this question blocks or constrains specific test cases. Does **not** block the suite when `ready_for_test_generation` is `true`. |
| `blocking_for_entire_suite` | Boolean | Yes (1.1+) | `true` if this question is a suite-level blocker and `ready_for_test_generation` must be `false`. Use sparingly. |
| `affected_acceptance_criteria` | Array of strings | No | AC-IDs affected by this question (e.g., `["AC-3", "AC-7"]`). Required when determinable and `blocking_for_specific_tests: true`. |
| `affected_test_areas` | Array of strings | No | Test areas affected (e.g., `["Boundary", "Lifecycle"]`). Required when determinable and `blocking_for_specific_tests: true`. |
| `blocking` | Boolean | Deprecated | Schema 1.0 field. Map to `blocking_for_specific_tests`. Emit only for backward compatibility. |
| `affects_ready` | Boolean | Deprecated | Schema 1.0 field. Map to `blocking_for_entire_suite`. Emit only for backward compatibility. |

| Attribute | Value |
|---|---|
| **Validation Rules** | `id` values must be unique within the array. `question` must not be empty. If `ready_for_test_generation` is `false`, at least one question must have `blocking_for_entire_suite: true` OR a suite blocker must be documented in `readiness.suite_blockers`. If `ready_for_test_generation` is `true`, no question may have `blocking_for_entire_suite: true` (VR-013). Material questions must not have both blocking flags set to `false`. |
| **Example** | `[{ "id": "Q-1", "question": "What matching threshold should be configured in the test environment for deterministic duplicate detection?", "blocking_for_specific_tests": true, "blocking_for_entire_suite": false, "affected_acceptance_criteria": ["AC-7"], "affected_test_areas": ["Boundary"] }]` |

---

### 5.14 `assumptions`

| Attribute | Value |
|---|---|
| **Description** | Every inference made during analysis that is not explicitly stated in the requirement or knowledge base. Each is labelled by type and cited where possible. |
| **Required** | Yes |
| **Type** | Array of Assumption objects. May be empty if no assumptions were made. |

**Assumption Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `id` | String | Yes | Sequential identifier: `"A-1"`, `"A-2"`, etc. |
| `text` | String | Yes | The assumption statement. |
| `type` | Enum string | Yes | `"Knowledge-Based"` or `"Unverified"`. |
| `source` | String | Conditional | Required when `type` is `"Knowledge-Based"`. The knowledge source citation (file name and section). Must be null or absent when `type` is `"Unverified"`. |
| `confidence` | Enum string | Yes | `"CERTAIN"`, `"INFERRED"`, or `"UNCERTAIN"`. |

| Attribute | Value |
|---|---|
| **Validation Rules** | `id` values must be unique. `type` must be one of the two allowed values. `source` must be present and non-empty when `type` is `"Knowledge-Based"`. `source` must be null or absent when `type` is `"Unverified"`. `confidence` must be one of the three allowed values. A `"Knowledge-Based"` assumption must not carry `confidence: "UNCERTAIN"`. |
| **Example** | `[{ "id": "A-1", "text": "The duplicate detection algorithm matches on email_address, first_name, last_name, and national_identifier.", "type": "Knowledge-Based", "source": "business-rules.md BR-011", "confidence": "CERTAIN" }, { "id": "A-2", "text": "The Supervisor notification is delivered via an in-portal alert banner.", "type": "Unverified", "source": null, "confidence": "UNCERTAIN" }]` |

---

### 5.15 `recommended_test_areas`

| Attribute | Value |
|---|---|
| **Description** | The test areas identified as applicable to this requirement. Used by the Test Generation Agent to scope test case generation and by the Validation Agent to check coverage completeness. |
| **Required** | Yes |
| **Type** | Array of Test Area objects. Must contain at least one entry with `applicable: true`. |

**Test Area Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `area` | Enum string | Yes | One of: `"Positive"`, `"Negative"`, `"Boundary"`, `"Permission"`, `"Lifecycle"`, `"Integration"`, `"Data Validation"`, `"Concurrency"`, `"Audit"`. |
| `applicable` | Boolean | Yes | `true` if this test area applies to the requirement; `false` if it does not. All nine areas must be represented. |
| `reason` | String | Yes | One sentence explaining why the area is or is not applicable. |

| Attribute | Value |
|---|---|
| **Validation Rules** | All nine defined test areas must appear exactly once. No duplicate `area` values. `reason` must be non-empty for every entry regardless of `applicable` value. At least one entry must have `applicable: true`. |
| **Example** | `[{ "area": "Positive", "applicable": true, "reason": "Happy-path creation and activation with no duplicate detected." }, { "area": "Permission", "applicable": true, "reason": "Activation requires Agent role; duplicate flag dismissal requires Supervisor role." }, { "area": "Concurrency", "applicable": false, "reason": "No concurrent state conflict is described or implied by this requirement." }]` |

---

### 5.16 `risk_level`

| Attribute | Value |
|---|---|
| **Description** | The overall risk classification of this requirement, reflecting the potential business impact of testing gaps or failures. |
| **Required** | Yes |
| **Type** | Enum string |
| **Allowed Values** | `"Low"`, `"Medium"`, `"High"`, `"Critical"` |
| **Validation Rules** | Must be exactly one of the four allowed values. Must be consistent with the risk criteria defined in the Requirement Analysis Agent (Section 8 Step 11): if any conflicts with a business rule are present, the level must be `"High"` or `"Critical"`. If compliance, consent, or irreversible operations are involved, the level must be `"Critical"`. |
| **Example** | `"High"` |

---

### 5.17 `risk_reason`

| Attribute | Value |
|---|---|
| **Description** | A written justification for the assigned `risk_level`. Must explain the specific factors that determined the level — not a restatement of the risk level name. |
| **Required** | Yes |
| **Type** | String |
| **Allowed Values** | Any non-empty string. Minimum 2 sentences. Maximum 8 sentences. |
| **Validation Rules** | Must not be empty. Must not be whitespace-only. Must not contain placeholder text. Must be internally consistent with the `risk_level` value — a `"Low"` risk_level must not cite conflicts with business rules or compliance concerns in its reason. |
| **Example** | `"This requirement involves the Pending → Active lifecycle transition, which is governed by duplicate detection (BR-004, BR-015) and downstream system notification (BR-022). A failure in this flow would allow duplicate Active customer records to enter the system, corrupting billing, communications, and compliance reporting. The involvement of multiple downstream systems and an irreversible activation event elevates the risk to High."` |

---

### 5.18 `confidence`

| Attribute | Value |
|---|---|
| **Description** | The overall epistemic confidence of this analysis object — reflecting how certain the agent is about the completeness and accuracy of its analysis as a whole. This is a summary-level label; individual field-level confidence is tracked in `assumptions`. |
| **Required** | Yes |
| **Type** | Enum string |
| **Allowed Values** | `"CERTAIN"`, `"INFERRED"`, `"UNCERTAIN"` |
| **Validation Rules** | Must be exactly one of the three allowed values. Must be consistent with the content of `assumptions` and `unresolved_questions`: if any assumption has `confidence: "UNCERTAIN"` or any question has `blocking_for_entire_suite: true`, the object-level `confidence` must be `"INFERRED"` or `"UNCERTAIN"`, never `"CERTAIN"`. Questions with `blocking_for_specific_tests: true` alone do not require object-level `confidence: "UNCERTAIN"`. |
| **Example** | `"INFERRED"` |

---

### 5.19 `ready_for_test_generation`

| Attribute | Value |
|---|---|
| **Description** | A boolean gate field read by the Orchestrator to determine whether the workflow may proceed to the Test Generation Agent. `true` means sufficient grounded information exists to produce a useful mix of READY, CONSTRAINED, and BLOCKED test cases. `false` means suite-level preconditions fail and human input is required before proceeding. |
| **Required** | Yes |
| **Type** | Boolean |
| **Allowed Values** | `true` or `false` |
| **Validation Rules** | Set `false` only when any of the following are true: (1) the requirement is empty, too short, or contradictory at its core; (2) no acceptance criterion in `acceptance_criteria_status` is `"Testable"` or `"Partially Testable"`; (3) the primary workflow cannot be identified; (4) safe test generation would require inventing most expected behaviour; (5) any question in `unresolved_questions` has `blocking_for_entire_suite: true`; (6) a Critical conflict in `conflicts` makes the primary success condition untestable. Set `true` when at least one AC is testable or partially testable, the business objective is clear, impacted rules and entities are identifiable, and unresolved questions can be isolated to specific tests. Do **not** set `false` solely because of Partially Testable ACs, non-critical conflicts, test-level open questions, or High/Critical risk level alone. |
| **Example** | `true` |

---

### 5.20 `blocker_reason` (Conditionally Required)

| Attribute | Value |
|---|---|
| **Description** | A human-readable explanation of why `ready_for_test_generation` is `false`. Lists the specific blocking conditions. |
| **Required** | Conditionally — required when `ready_for_test_generation` is `false`; must be absent or null when `ready_for_test_generation` is `true`. |
| **Type** | String |
| **Allowed Values** | Any non-empty string when present. |
| **Validation Rules** | Must be present and non-empty when `ready_for_test_generation` is `false`. Must be absent or null when `ready_for_test_generation` is `true`. |
| **Example** | `"No testable acceptance criteria. All ACs are Not Testable and the primary workflow cannot be identified."` |

---

### 5.21 `readiness` (Optional — schema 1.1+)

| Attribute | Value |
|---|---|
| **Description** | Structured readiness summary distinguishing suite-level blockers from the expected mix of test outcomes. Helps the Test Generation Agent plan READY, CONSTRAINED, and BLOCKED tests. |
| **Required** | No — recommended for all objects produced against schema 1.1+. |
| **Type** | Readiness object |

**Readiness Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `suite_blockers` | Array of strings | Yes when present | Empty array when `ready_for_test_generation: true`. One or more concise reasons when `false`. |
| `expected_generation_mix` | Object | No | Summary of anticipated test outcomes when `ready_for_test_generation: true`. |
| `expected_generation_mix.ready` | String | No | Brief description of tests that can proceed with full expected results. |
| `expected_generation_mix.constrained` | String | No | Tests with partial coverage limited by LIMs, partial ACs, or inferred behaviour. |
| `expected_generation_mix.blocked` | String | No | Tests requiring resolution of specific Q-IDs before expected results are determinable. |

| Attribute | Value |
|---|---|
| **Validation Rules** | When `ready_for_test_generation: true`, `suite_blockers` must be an empty array. When `false`, `suite_blockers` must contain at least one non-empty string. |
| **Example** | `{ "suite_blockers": [], "expected_generation_mix": { "ready": "AC-1, AC-2, AC-6, AC-8 permission and lifecycle tests", "constrained": "AC-7 boundary tests citing LIM-031", "blocked": "Duplicate Flag persistence data-state tests pending Q-1" } }` |

---

### 5.22 `conflicts` (Optional)

| Attribute | Value |
|---|---|
| **Description** | Detected contradictions between the requirement and the knowledge base, or internal contradictions within the requirement itself. |
| **Required** | No |
| **Type** | Array of Conflict objects. Empty array when no conflicts exist. |

**Conflict Object fields:**

| Sub-field | Type | Required | Description |
|---|---|---|---|
| `id` | String | Yes | Sequential identifier: `"CON-1"`, `"CON-2"`, etc. |
| `requirement_text` | String | Yes | The verbatim fragment of the requirement that conflicts. |
| `conflicts_with` | String | Yes | The BR-ID, LIM-ID, or glossary term reference it conflicts with. |
| `nature` | String | Yes | One sentence describing the nature of the conflict. |
| `severity` | Enum string | Yes | `"Critical"` — directly contradicts a business rule; `"High"` — inconsistent with a limitation; `"Medium"` — terminology conflict. |

| Attribute | Value |
|---|---|
| **Validation Rules** | `id` values must be unique. `conflicts_with` must reference a real BR-ID or LIM-ID if it is one. `severity` must be one of the three allowed values. |
| **Example** | `[{ "id": "CON-1", "requirement_text": "The Agent may bypass duplicate detection if the record is needed urgently.", "conflicts_with": "BR-004", "nature": "BR-004 states that duplicate detection must run before activation with no bypass mechanism defined.", "severity": "Critical" }]` |

---

## 6. Validation Rules

The following rules must be enforced by any consumer reading a Requirement Analysis Object before processing it. A consumer must reject an invalid object rather than processing it with unknown results.

| ID | Rule | Effect of Violation |
|---|---|---|
| VR-001 | `schema_version` must be present and match the pattern `^\d+\.\d+$`. | Reject object. |
| VR-002 | `requirement_id` must be present, non-empty, and non-whitespace. | Reject object. |
| VR-003 | `requirement_summary` must be between 20 and 200 words inclusive. | Reject object. |
| VR-004 | `actors` must contain at least one entry. Every entry must have a non-empty `actor` and a valid `role` value. | Reject object. |
| VR-005 | Every `id` in `impacted_business_rules` must exist in `business-rules.md`. An ID that does not exist in the knowledge base renders the object invalid. | Reject object. |
| VR-006 | Every `id` in `relevant_limitations` must exist in `known-limitations.md`. An ID that does not exist in the knowledge base renders the object invalid. | Reject object. |
| VR-007 | Every `entity` in `impacted_entities` must exist in `data-model.md`. | Reject object. |
| VR-008 | Every `entity` + `field` combination in `impacted_fields` must exist in `data-model.md`. The field must belong to the named entity. | Reject object. |
| VR-009 | `confidence` must be exactly `"CERTAIN"`, `"INFERRED"`, or `"UNCERTAIN"`. | Reject object. |
| VR-010 | `risk_level` must be exactly `"Low"`, `"Medium"`, `"High"`, or `"Critical"`. | Reject object. |
| VR-011 | `ready_for_test_generation` must be Boolean `true` or `false`. Any other value type (e.g., string `"true"`) is invalid. | Reject object. |
| VR-012 | If `ready_for_test_generation` is `false`, `blocker_reason` must be present and non-empty. | Reject object. |
| VR-013 | If `ready_for_test_generation` is `true`, no question in `unresolved_questions` may have `blocking_for_entire_suite: true`. For schema 1.0 objects, no question may have `affects_ready: true`. | Reject object. |
| VR-014 | If `ready_for_test_generation` is `true`, `blocker_reason` must be absent or null. | Reject object. |
| VR-015 | If any conflict in `conflicts` has `severity: "Critical"` **and** the conflict makes the primary success condition untestable, `ready_for_test_generation` must be `false`. Non-critical conflicts and critical conflicts that affect only specific tests do not require `false`. | Reject object if violated. |
| VR-016 | `recommended_test_areas` must contain exactly nine entries — one for each defined test area — with no duplicates. | Reject object. |
| VR-017 | At least one entry in `recommended_test_areas` must have `applicable: true`. | Reject object. |
| VR-018 | If object-level `confidence` is `"CERTAIN"`, no assumption may have `type: "Unverified"` or `confidence: "UNCERTAIN"`. | Reject object. |
| VR-019 | Every `source` field on a `"Knowledge-Based"` assumption must be a non-empty string. | Reject object. |
| VR-020 | `risk_reason` must be present and non-empty when `risk_level` is any value. | Reject object. |
| VR-021 | If `risk_level` is `"Critical"`, at least one of the following must be true: a conflict exists in `conflicts`; a compliance field (consent, national_identifier, audit) appears in `impacted_fields`; or an irreversible operation (merge, closure) appears in `impacted_features`. | Warn — do not reject; flag for human review. |
| VR-022 | `acceptance_criteria_status` must contain at least one entry. If the requirement has no AC, it must contain the sentinel entry `AC-0` with `classification: "Not Testable"`. | Reject object. |
| VR-023 | `missing_information` must be present and non-empty in any Acceptance Criterion Status where `classification` is `"Partially Testable"` or `"Not Testable"`. | Reject object. |
| VR-024 | Schema 1.1+ Question objects must include `blocking_for_specific_tests` and `blocking_for_entire_suite`. Schema 1.0 objects may use deprecated `blocking` and `affects_ready`; consumers must map per Section 9. | Reject 1.1+ objects missing new fields. |
| VR-025 | If `readiness` is present and `ready_for_test_generation: true`, `readiness.suite_blockers` must be an empty array. | Reject object. |
| VR-026 | Material questions must not have both `blocking_for_specific_tests: false` and `blocking_for_entire_suite: false`. | Warn — flag for human review. |

---

## 7. Required Relationships

The following cross-field relationships are binding constraints on the object as a whole. These cannot be validated by examining any single field in isolation.

| Relationship | Rule |
|---|---|
| **R-01: BR-ID existence** | Every `id` in `impacted_business_rules` must correspond to a real rule in the active version of `business-rules.md`. The Requirement Analysis Agent is responsible for this at generation time. The Orchestrator must re-validate before invoking the Test Generation Agent. |
| **R-02: LIM-ID existence** | Every `id` in `relevant_limitations` must correspond to a real limitation in the active version of `known-limitations.md`. Same validation responsibility as R-01. |
| **R-03: Entity-field coherence** | Every `entity` value in `impacted_fields` must appear in `impacted_entities`. An impacted field cannot belong to an entity that is not itself listed as impacted. |
| **R-04: Suite-level question gate** | If any question in `unresolved_questions` has `blocking_for_entire_suite: true` (or deprecated `affects_ready: true` on schema 1.0 objects), then `ready_for_test_generation` must be `false`. Questions with `blocking_for_specific_tests: true` alone do not trigger this gate. |
| **R-05: Critical conflict gate** | If any entry in `conflicts` has `severity: "Critical"` **and** the conflict makes the requirement's primary success condition untestable, then `ready_for_test_generation` must be `false`. Conflicts that affect only specific tests route to CONSTRAINED or BLOCKED tests instead. |
| **R-06: Confidence-readiness coherence** | Object-level `confidence: "UNCERTAIN"` is permitted when `ready_for_test_generation: true` if sufficient testable scope remains and uncertainty is isolated to specific tests or assumptions. Object-level `confidence: "UNCERTAIN"` with `ready_for_test_generation: false` indicates the analysis as a whole cannot support safe generation. |
| **R-07: Not-Testable AC gate** | If **all** acceptance criteria in `acceptance_criteria_status` are `"Not Testable"`, or a **core** AC (primary success condition) is `"Not Testable"` **and** no other AC is `"Testable"` or `"Partially Testable"`, then `ready_for_test_generation` must be `false`. A mix of Testable/Partially Testable and Not Testable non-core ACs does not block the suite. |
| **R-08: Assumption-confidence coherence** | A `"Knowledge-Based"` assumption must not carry `confidence: "UNCERTAIN"`. If the source is cited, the confidence is at minimum `"INFERRED"`. |
| **R-09: Blocker presence** | `blocker_reason` must be present if and only if `ready_for_test_generation` is `false`. It must be absent if and only if `ready_for_test_generation` is `true`. |
| **R-10: Test area completeness** | `recommended_test_areas` must contain exactly one entry per defined test area (nine total). The Validation Agent uses this as the authoritative scope for coverage assessment. |

---

## 8. Example Object

The following is a complete, valid Requirement Analysis Object for a fictional user story about duplicate customer detection. It is intended to illustrate correct structure, value formats, and relationship coherence — not to describe a real requirement.

```yaml
schema_version: "1.1"
requirement_id: "US-042"
requirement_source: "knowledge/requirements/duplicate-customer-story.md"
analysis_date: "2026-07-24"
domain_context: "Customer Management Portal"

requirement_summary: >
  When a user with Agent role creates a new customer record whose primary email
  address matches an existing Active customer record, the system must automatically
  raise a duplicate flag. The new record must remain in Pending status. The Agent
  must not be able to activate the record. A user with Supervisor role must review
  the flagged record and either dismiss the flag with a written reason or initiate
  a merge before the record can proceed to Active.

business_objective: >
  Prevent duplicate Active customer records by gating activation on automated
  duplicate detection and Supervisor authorisation, preserving the integrity
  of the organisation's customer master data.

actors:
  - actor: "Customer Service Representative"
    role: "Agent"
    source: "application-context.md Section 3; glossary.md — Agent Role"
  - actor: "Team Lead"
    role: "Supervisor"
    source: "application-context.md Section 3; glossary.md — Supervisor Role"

impacted_features:
  - "Customer record management"
  - "Duplicate detection"
  - "Account status management"

impacted_business_rules:
  - id: "BR-002"
    title: "Unique Email on Creation"
    relevance: "Matching primary email triggers the duplicate detection path."
    relationship: "Exercised"
  - id: "BR-004"
    title: "Duplicate Check Before Activation"
    relevance: "Duplicate detection must run and pass before Pending → Active is permitted."
    relationship: "Exercised"
  - id: "BR-011"
    title: "Automatic Duplicate Flagging"
    relevance: "Matching email automatically raises a duplicate flag at creation time."
    relationship: "Exercised"
  - id: "BR-014"
    title: "Duplicate Dismissal Requires Authorization"
    relevance: "Only a Supervisor can dismiss the flag; Agent cannot clear it."
    relationship: "Exercised"
  - id: "BR-015"
    title: "Duplicate Flag Blocks Activation"
    relevance: "The Pending → Active transition is blocked while the flag is open."
    relationship: "Exercised"
  - id: "BR-038"
    title: "Role-Based Access Enforcement"
    relevance: "Agent must be denied the activation action while the flag is open."
    relationship: "Constrained by"

impacted_entities:
  - entity: "Customer"
    operations: ["Create", "Validate", "Transition"]
    source: "data-model.md Section 1"
  - entity: "Email"
    operations: ["Create", "Validate"]
    source: "data-model.md Section 3"
  - entity: "Customer Status History"
    operations: ["Create"]
    source: "data-model.md Section 6"
  - entity: "Audit Event"
    operations: ["Create"]
    source: "data-model.md Section 8"

impacted_fields:
  - entity: "Customer"
    field: "status"
    operation: "Validate"
    constraint: "Must remain Pending while duplicate flag is open; BR-015"
    sensitive: false
  - entity: "Customer"
    field: "created_by"
    operation: "Create"
    constraint: "Must reference a valid Agent or above user"
    sensitive: false
  - entity: "Email"
    field: "email_address"
    operation: "Validate"
    constraint: "RFC 5321 format; max 254 chars; must be unique across Active and Pending primary emails; BR-002"
    sensitive: true
  - entity: "Email"
    field: "email_type"
    operation: "Validate"
    constraint: "Uniqueness constraint applies only to Primary type; LIM-008"
    sensitive: false

relevant_limitations:
  - id: "LIM-008"
    title: "Secondary Contact Methods Are Not Deduplicated"
    impact: "Duplicate detection tests must use primary email addresses only; secondary email duplicates do not trigger a flag."
  - id: "LIM-031"
    title: "Duplicate Detection Sensitivity Is Configurable and Environment-Specific"
    impact: "Tests must verify the matching threshold is correctly configured in the test environment before asserting duplicate flag behaviour."

acceptance_criteria_status:
  - id: "AC-1"
    text: "Given a new customer record is created with a primary email matching an existing Active customer, when the record is saved, then a duplicate flag must be automatically raised."
    classification: "Testable"
    missing_information: null
  - id: "AC-2"
    text: "An Agent must not be able to activate a record with an open duplicate flag."
    classification: "Testable"
    missing_information: null
  - id: "AC-3"
    text: "A Supervisor must be able to dismiss the flag with a written reason, after which the record may proceed to Active."
    classification: "Testable"
    missing_information: null
  - id: "AC-4"
    text: "The system should notify relevant users when a duplicate flag is raised."
    classification: "Partially Testable"
    missing_information: "The notification mechanism and the definition of 'relevant users' are not specified. Q-1 must be resolved before a test can be written for this criterion."

ambiguities:
  - id: "AMB-1"
    description: "AC-4 states the system 'should notify relevant users' but does not specify the notification mechanism (in-portal alert, email, system event) or which users qualify as 'relevant'."
    affected_criteria: ["AC-4"]

unresolved_questions:
  - id: "Q-1"
    question: "What matching threshold should be configured in the test environment for deterministic duplicate detection assertions?"
    blocking_for_specific_tests: true
    blocking_for_entire_suite: false
    affected_acceptance_criteria: ["AC-7"]
    affected_test_areas: ["Boundary"]
  - id: "Q-2"
    question: "What specific fields must appear in the Supervisor duplicate comparison view per AC-3?"
    blocking_for_specific_tests: true
    blocking_for_entire_suite: false
    affected_acceptance_criteria: ["AC-3"]
    affected_test_areas: ["Positive"]

assumptions:
  - id: "A-1"
    text: "Duplicate detection matches on primary email_address as described in BR-002. Additional matching fields (name, national_identifier) may also apply per BR-011, but email uniqueness alone is the trigger described in this requirement."
    type: "Knowledge-Based"
    source: "business-rules.md BR-002, BR-011"
    confidence: "CERTAIN"
  - id: "A-2"
    text: "The duplicate flag is raised automatically at creation time, not only at activation time, based on the workflow described in BR-011."
    type: "Knowledge-Based"
    source: "business-rules.md BR-011"
    confidence: "CERTAIN"
  - id: "A-3"
    text: "The notification described in AC-4 is an in-portal alert. This is not stated in the requirement or the knowledge base."
    type: "Unverified"
    source: null
    confidence: "UNCERTAIN"

recommended_test_areas:
  - area: "Positive"
    applicable: true
    reason: "Happy path: create record with unique email, no flag raised, Agent activates successfully."
  - area: "Negative"
    applicable: true
    reason: "Create record with duplicate primary email; confirm flag is raised and activation is blocked."
  - area: "Boundary"
    applicable: true
    reason: "Email address at exactly 254 characters; email with borderline format validity."
  - area: "Permission"
    applicable: true
    reason: "Agent cannot dismiss the flag; Supervisor can dismiss with a reason; Viewer cannot access the record in this state."
  - area: "Lifecycle"
    applicable: true
    reason: "Pending → Active transition must be blocked when flag is open; allowed after flag is dismissed."
  - area: "Integration"
    applicable: false
    reason: "No downstream integration event is specified in the requirement for duplicate flag creation or dismissal."
  - area: "Data Validation"
    applicable: true
    reason: "Email address format and uniqueness constraints must be validated."
  - area: "Concurrency"
    applicable: false
    reason: "No concurrent access conflict is described or implied by this requirement."
  - area: "Audit"
    applicable: true
    reason: "Duplicate flag creation and dismissal must produce audit events per BR-043."

risk_level: "High"

risk_reason: >
  This requirement governs the duplicate detection activation gate, which is the
  primary control preventing duplicate Active customer records from entering the
  system. A failure in this flow — particularly in role-based access enforcement
  for flag dismissal or the Pending → Active gate — would allow duplicates to
  proliferate, corrupting billing, communications, and compliance reporting.
  The involvement of multiple business rules (BR-002, BR-004, BR-011, BR-014,
  BR-015, BR-038), a lifecycle transition, and an unresolved notification question
  (Q-1) elevates this to High risk.

confidence: "INFERRED"

ready_for_test_generation: true

blocker_reason: null

readiness:
  suite_blockers: []
  expected_generation_mix:
    ready: "AC-1, AC-2, AC-6, AC-8 — creation, flagging, permission rejection, activation gate"
    constrained: "AC-7 boundary tests citing LIM-031; AC-3 partial display assertions"
    blocked: "Duplicate detection threshold precision tests pending Q-1; full AC-3 field list tests pending Q-2"

conflicts: []
```

---

## 9. Backward Compatibility Rules

These rules govern how consumers must behave when the `schema_version` of an object does not exactly match the version they were built against.

| Scenario | Consumer Behaviour |
|---|---|
| `schema_version` matches exactly | Process normally. |
| `schema_version` has the same major version but a higher minor version (e.g., consumer is `1.0`, object is `1.2`) | Accept the object. Ignore fields not defined in the consumer's version. Do not fail on unknown optional fields. |
| `schema_version` has the same major version but a lower minor version (e.g., consumer is `1.2`, object is `1.0`) | Accept the object. Treat any fields defined in the consumer's version but absent in the object as optional-absent. Apply defaults where defined in Section 4. |
| `schema_version` has a higher major version (e.g., consumer is `1.x`, object is `2.0`) | Reject the object. Return: `INCOMPATIBLE_SCHEMA: Consumer supports schema major version 1; object was produced against major version 2. Update the consumer before processing.` |
| `schema_version` has a lower major version (e.g., consumer is `2.0`, object is `1.0`) | Reject the object. Return: `INCOMPATIBLE_SCHEMA: Object was produced against schema major version 1; consumer requires major version 2. Re-run the Requirement Analysis Agent with the current schema.` |
| `schema_version` is absent | Treat as version `"1.0"`. Log a warning: `schema_version field is absent. Assuming 1.0. Re-run analysis to produce a versioned object.` |
| `schema_version` is present but malformed (does not match `^\d+\.\d+$`) | Reject the object per VR-001. |

**Field addition policy (minor version increment):**
- New optional fields may be added in a minor version increment.
- New required fields may only be added in a major version increment.
- Existing fields may not be removed in a minor version increment.
- Existing field `allowed values` may not be reduced in a minor version increment (values may be added but not removed).

**Schema 1.0 → 1.1 deprecated field mapping:**

Consumers reading schema 1.0 Question objects must apply this mapping before enforcing readiness rules:

| Schema 1.0 field | Maps to (1.1) |
|---|---|
| `blocking: true` | `blocking_for_specific_tests: true`, `blocking_for_entire_suite: false` |
| `blocking: false` | `blocking_for_specific_tests: false`, `blocking_for_entire_suite: false` |
| `affects_ready: true` | `blocking_for_entire_suite: true` (and typically `blocking_for_specific_tests: true`) |
| `affects_ready: false` | No effect on `blocking_for_entire_suite` |

Producers emitting schema 1.1 objects should prefer the new fields and may include deprecated fields only as mirrors for backward compatibility.

**Field removal policy (major version increment):**
- Any field removal, rename, or reduction of allowed values requires a major version increment.
- A migration guide must accompany any major version increment, documenting every breaking change and the required transformation from the previous major version.
