I'll now execute the Requirement Analysis Agent for US-042. Let me work through all 14 analysis steps methodically after reading all knowledge sources.

---

# Requirement Analysis

**Requirement ID:** US-042
**Requirement Source:** knowledge/requirements/duplicate-customer-story.md
**Analysis Date:** 2026-07-24
**Risk Level:** High

---

## Requirement Summary

US-042 requires that when a user with Agent role submits a new customer creation request, the system automatically runs duplicate detection against all Active and Pending customer records before saving the record. If one or more potential matches are found, the system must raise a Duplicate Flag on the new record and retain its status as Pending, preventing it from transitioning to Active. A Supervisor (not an Agent) must then review the flagged record alongside the matching records, and may either dismiss the flag with a written reason (allowing the record to proceed to Active subject to all other activation requirements) or initiate a merge, designating a survivor record, which causes the non-survivor to be set to Merged status, linked to the survivor, and all downstream systems notified. If an Agent attempts either action (dismissal or merge), the system must reject it and return an error message indicating Supervisor authorisation is required. Additionally, if an Agent attempts to transition a Pending record with an open Duplicate Flag to Active, that transition must also be rejected. Duplicate detection evaluates first name, last name, primary email, primary phone, and national identifier (when present on both records). This story covers only the creation-triggered detection path; update-triggered detection (BR-012) is explicitly out of scope.

---

## Business Objective

To maintain a single, accurate, deduplicated customer record as the organisation's source of truth (application-context.md Section 11 — Data integrity), by preventing potentially duplicate records from reaching Active status without authorised Supervisor review.

---

## Actors and Roles

| Actor | Mapped Role | Source |
|---|---|---|
| Customer Service Agent | Agent | glossary.md — Agent (Role); application-context.md Section 4 |
| Supervisor | Supervisor | glossary.md — Supervisor (Role); application-context.md Section 4 |
| System (duplicate detection engine) | System | application-context.md Section 4; glossary.md — Agent (Role) note on System (Role) |

No unmapped actors detected. All actors are present in the defined role set.

---

## Impacted Features

- Customer record management (application-context.md Section 5)
- Duplicate detection (application-context.md Section 5)
- Customer merge (application-context.md Section 5)
- Account status management (application-context.md Section 5)
- Activity and audit history (application-context.md Section 5)

---

## Impacted Business Rules

| Rule ID | Title | Relevance | Relationship |
|---|---|---|---|
| BR-001 | Mandatory Fields on Creation | New customer creation requires first name, last name, at least one contact method, and customer type — fields that also serve as duplicate detection inputs. | Exercised |
| BR-003 | Agent Role Required for Creation | The requirement states the initiating actor is a logged-in Agent; BR-003 governs which roles may create records. | Exercised |
| BR-004 | Duplicate Check Before Activation | The requirement mandates duplicate detection before a record can transition from Pending to Active. | Exercised |
| BR-005 | System-Generated Customer ID | A new customer record created under this flow will be assigned a system-generated immutable ID at creation. | Exercised |
| BR-006 | Initial Status is Pending | AC-2 requires the new record's status to remain Pending after flagging — consistent with BR-006, which governs all new records. | Exercised |
| BR-008 | National ID Field Restricted | AC-7 includes national identifier as a duplicate detection field; BR-008 restricts which roles can view/edit this field, which constrains how the comparison view (AC-3) can display it to a Supervisor. | Constrained by |
| BR-009 | One Record Per Verified Identity | The underlying business rule that the duplicate detection workflow enforces; no two Active records may represent the same verified identity. | Exercised |
| BR-011 | Automatic Duplicate Flagging | AC-1 and AC-2 directly exercise this rule — automatic evaluation of every new record against Active and Pending records, using configurable matching including name, email, phone, and national identifier. | Exercised |
| BR-014 | Duplicate Dismissal Requires Authorization | AC-4 and AC-6 directly exercise this rule — only a Supervisor may dismiss the flag; dismissal must include a written reason. | Exercised |
| BR-015 | Duplicate Flag Blocks Activation | AC-8 directly exercises this rule — a Pending record with an open Duplicate Flag cannot transition to Active. | Exercised |
| BR-016 | Allowed Status Transitions | The requirement involves the Pending → Active transition (blocked while flag is open) and the Merged status transition (after merge completion). Both must follow the permitted matrix. | Exercised |
| BR-022 | Status Change Propagated to Downstream | AC-5 requires that all downstream systems are notified when a merge is completed and the non-survivor transitions to Merged status. | Exercised |
| BR-032 | Merge Requires Supervisor Authorization | AC-5 and AC-6 exercise this rule — only a Supervisor may initiate a merge; an Agent attempting a merge must be rejected. | Exercised |
| BR-033 | Merge Designates One Survivor | AC-5 requires the Supervisor to designate the survivor record during a merge. | Exercised |
| BR-034 | Merge is Irreversible | The Notes section of the requirement explicitly states the merge operation is irreversible, consistent with this rule. | Exercised |
| BR-035 | Non-Survivor Retained for Audit | AC-5 requires the non-survivor record to be set to Merged status and linked to the survivor — retained per this rule. | Exercised |
| BR-036 | Only One Active Merge Per Record | If a record flagged as a duplicate is already subject to an in-progress merge, a second merge must be rejected. | Constrained by |
| BR-037 | Downstream Systems Notified on Merge | AC-5 explicitly requires notification of all downstream systems on merge completion. | Exercised |
| BR-038 | Role-Based Access Enforcement | AC-6 requires that Agent role actions (dismiss or merge) are rejected; role enforcement underlies all permission-based ACs. | Exercised |
| BR-039 | Restricted Fields Require Elevated Role | AC-7 includes national identifier as a matching field; the comparison view (AC-3) must respect field-level restrictions — Agents cannot view national identifier. | Constrained by |
| BR-043 | All Changes Produce Audit Entries | Flag creation, dismissal, and merge operations must all produce audit entries. | Exercised |
| BR-051 | Validation Errors Returned with Field-Level Detail | AC-6 and AC-8 require clear error messages when the Agent's actions are rejected. | Exercised |
| BR-052 | Rejected Transitions Return Business Reason | AC-8 requires a specific message when Pending → Active is rejected due to an open flag. | Exercised |
| BR-056 | Duplicate Resolution Rate is a Tracked Metric | The duplicate resolution workflow exercised by this story contributes to the metrics tracked under this rule. | Constrained by |

---

## Impacted Entities and Fields

### Customer

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `customer_id` | Create (Read) | System-generated; UUID; immutable; globally unique — BR-005, BR-007 | data-model.md Section 1 |
| `customer_type` | Create | `Individual` or `Organisation`; mandatory; immutable after creation — LIM-002 | data-model.md Section 1 |
| `first_name` | Create / Validate | 1–100 chars; not whitespace-only; not null; applies when `customer_type = Individual` — BR-048 | data-model.md Section 1 |
| `last_name` | Create / Validate | 1–150 chars; not whitespace-only; not null; applies when `customer_type = Individual` — BR-048 | data-model.md Section 1 |
| `national_identifier` | Read / Validate | Optional; 5–20 alphanumeric chars; unique across non-Merged/non-Closed records when provided; restricted field (Supervisor/Administrator only) — BR-008, BR-039 | data-model.md Section 1 |
| `status` | Validate / Transition | New records start as `Pending` (BR-006); must not transition to `Active` while Duplicate Flag is open (BR-015); transitions to `Merged` for non-survivor (BR-033, BR-035); must follow BR-016 transition matrix | data-model.md Section 1 |
| `created_by` | Create | Must reference a valid User or system identity with Agent role or above — BR-003 | data-model.md Section 1 |
| `merged_into` | Update | Required if `status = Merged`; must reference the surviving customer record — BR-010, BR-035 | data-model.md Section 1 |

### Email

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `email_address` | Create / Validate | RFC 5321 format; max 254 chars; lowercased on save; must be unique across Active and Pending records for `email_type = Primary` — BR-002, BR-024 | data-model.md Section 3 |
| `email_type` | Validate | Uniqueness constraint applies to `Primary` only; `Secondary` not deduplicated — LIM-008 | data-model.md Section 3 |
| `is_verified` | Validate | Required `true` with populated `verified_at` for Pending → Active transition — BR-023 | data-model.md Section 3 |

### Phone

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `phone_number` | Create / Validate | E.164 format; max 15 digits; unique across Active and Pending for `phone_type = Primary` — BR-025, BR-026 | data-model.md Section 4 |
| `phone_type` | Validate | Uniqueness constraint applies to `Primary` only; `Secondary` not deduplicated — LIM-008 | data-model.md Section 4 |

### Merge History

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `merge_id` | Create | System-generated UUID; unique globally | data-model.md Section 7 |
| `survivor_customer_id` | Create | Must reference an Active Customer after merge; distinct from `non_survivor_customer_id` | data-model.md Section 7 |
| `non_survivor_customer_id` | Create | Must reference the Customer transitioning to Merged; can appear as non-survivor in at most one Merge History record — BR-036 | data-model.md Section 7 |
| `initiated_by` | Create | Must reference a User with Supervisor role or above — BR-032 | data-model.md Section 7 |
| `confirmed_by` | Create | Must reference a User with Supervisor role or above — BR-032 | data-model.md Section 7 |
| `merge_notes` | Create | Optional; 0–2000 chars | data-model.md Section 7 |

### Customer Status History

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `status_history_id` | Create | System-generated; immutable | data-model.md Section 6 |
| `customer_id` | Create | Must reference the transitioning Customer record | data-model.md Section 6 |
| `previous_status` | Create | `Pending` for the creation-triggered paths in this story | data-model.md Section 6 |
| `new_status` | Create | Must be a permitted transition from `previous_status` per BR-016 | data-model.md Section 6 |
| `reason_code` | Create | Required for transitions to `Suspended` and `Closed`; not required for Pending → Active or Pending → Merged | data-model.md Section 6 |
| `changed_by` | Create | Must reference a valid User or system identity | data-model.md Section 6 |

### Audit Event

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `audit_id` | Create | System-generated; unique; immutable — BR-044 | data-model.md Section 8 |
| `entity_type` | Create | `Customer`, `MergeHistory` for events in this workflow | data-model.md Section 8 |
| `action` | Create | `CREATE`, `STATUS_CHANGE`, `MERGE` applicable to this workflow — BR-043 | data-model.md Section 8 |
| `performed_by` | Create | Must reference the acting User or system identity | data-model.md Section 8 |
| `performed_at` | Create | UTC; system-assigned; immutable | data-model.md Section 8 |

---

## Relevant Known Limitations

| Limitation ID | Title | Impact on Requirement or Testing |
|---|---|---|
| LIM-004 | No Bulk Customer Creation | All test scenarios must use individual record creation; no batch creation path exists to test. |
| LIM-008 | Secondary Contact Methods Are Not Deduplicated | Duplicate detection tests must use primary email and primary phone only; adding duplicate secondary contact methods must not trigger a flag and should be tested as a negative/boundary case. |
| LIM-015 | Merge Cannot Be Partially Reversed | Test scenarios must not expect a merge reversal option; generate tests confirming the non-survivor remains in Merged status post-completion with no undo capability. |
| LIM-016 | Merge Does Not Automatically Resolve Data Conflicts | Tests for the merge path (AC-5) must not expect automatic field selection; the Supervisor must be presented with both records' values to choose from — automated field overwrite must not be asserted. |
| LIM-017 | Only Two Records Can Be Merged in a Single Operation | Merge tests are scoped to exactly two records; submitting three or more records in a single merge request is an out-of-scope negative scenario (but worth flagging as a rejection test). |
| LIM-024 | Downstream Systems Are Notified Asynchronously | AC-5 requires downstream notification; tests must account for asynchronous delivery and must not assert immediate downstream state change — event receipt via stub must be verified with polling. |
| LIM-030 | Test Environments Do Not Receive Live Downstream Events | Integration tests for AC-5 downstream notification must use stub or mock downstream systems; real downstream processing cannot be verified in non-production environments. |
| LIM-031 | Duplicate Detection Sensitivity Is Configurable and Environment-Specific | Duplicate detection tests (AC-1, AC-7) must document expected threshold configuration; test results may vary by environment if thresholds differ — tests must verify configuration before asserting flag behaviour. |

---

## Acceptance Criteria Assessment

| # | Criterion | Classification | Missing Information |
|---|---|---|---|
| AC-1 | Given I am a logged-in Agent, when I submit a new customer creation request, then the system must automatically run duplicate detection against all Active and Pending customer records before the record is saved. | Testable | None |
| AC-2 | Given duplicate detection identifies one or more potential matches, when the new customer record is created, then the system must raise a Duplicate Flag on the new record and retain its status as Pending. | Testable | None — the Duplicate Flag entity is implied by the glossary and BR-011; however, the precise data field or record used to represent the Duplicate Flag is not defined in data-model.md (see Ambiguity AMB-1). |
| AC-3 | Given a Duplicate Flag exists on a Pending record, when a Supervisor opens the flagged record, then the system must display the list of matching records alongside the flagged record to support comparison and review. | Partially Testable | The specific fields that must be displayed in the comparison view are not defined. The requirement does not state whether national identifier (a restricted field under BR-008/BR-039) should be visible to a Supervisor in this view, or what "alongside" means in terms of UI layout. Without a defined field list, a pass/fail assertion for completeness of the comparison view cannot be written. |
| AC-4 | Given a Duplicate Flag is open on a Pending record, when a Supervisor dismisses the flag and provides a written reason, then the flag is cleared and the record becomes eligible to transition to Active, subject to all other activation requirements being met. | Testable | None — BR-014 and BR-015 fully govern dismissal and post-dismissal activation eligibility. |
| AC-5 | Given a Duplicate Flag is open on a Pending record, when a Supervisor initiates a merge and designates the survivor record, then the system must complete the merge, set the non-survivor record to Merged status, link the non-survivor to the survivor, and notify all downstream systems. | Partially Testable | Two elements are unresolved: (1) Survivor designation — the requirement does not specify which of the two records (the new Pending record or the existing Active/Pending record) may be designated as the survivor, or whether either is permitted. BR-033 requires designation but does not constrain which record can be the survivor. (2) Downstream notification content — the specific event schema sent to downstream systems is governed by LIM-026 (fixed integration contracts not described in the requirement or knowledge base accessible here). |
| AC-6 | Given a Duplicate Flag is open on a Pending record, when an Agent attempts to dismiss the flag or initiate a merge, then the system must reject the action and return a clear error message indicating that Supervisor authorisation is required. | Testable | None — BR-014, BR-032, BR-038, and BR-051 collectively govern this behaviour. |
| AC-7 | The duplicate detection algorithm must evaluate the following fields when comparing a new record against existing records: first name, last name, primary email address, primary phone number, and national identifier (when provided on both records being compared). | Partially Testable | The matching threshold and weighting applied to each field are configurable and environment-specific (LIM-031). Without knowing the configured thresholds, boundary tests for marginal matches (e.g., similar but not identical names) cannot assert a deterministic outcome. Exact-match tests are testable; near-match boundary tests are constrained by LIM-031. Additionally, "when provided on both records" is ambiguous — does detection skip national identifier comparison if only one record has it, or does it treat the absent value as non-matching? |
| AC-8 | Given a Pending record has an open Duplicate Flag, when an Agent attempts to transition the record to Active, then the system must reject the transition and return a message stating that an open Duplicate Flag must be resolved before activation. | Testable | None — BR-015 and BR-052 govern this behaviour. |

---

## Ambiguities and Missing Information

1. **AMB-1 — Duplicate Flag data representation:** The requirement refers to a "Duplicate Flag" being raised and cleared, but the data model (`data-model.md`) does not define a Duplicate Flag entity, field on the Customer entity, or any flag-related field. Where is the Duplicate Flag stored? Is it a field on the Customer record, a separate entity, or a status-based indicator? Without this, tests for data-state assertions (e.g., confirming the flag is present or cleared) cannot be written with certainty.

2. **AMB-2 — Survivor designation constraints (AC-5):** When a Supervisor initiates a merge from a flagged Pending record, can either record (the new Pending record or the existing Active/Pending match) be designated the survivor, or is there a rule constraining which record must survive? BR-033 requires designation but does not restrict which record may be chosen. If the existing Active record must always survive, tests that attempt to designate the Pending record as survivor need a defined expected outcome.

3. **AMB-3 — Comparison view field specification (AC-3):** The requirement states the system "must display the list of matching records alongside the flagged record to support comparison and review" but does not specify which fields must be visible in the comparison view. Does the view include restricted fields (national identifier) for the Supervisor? Does it include all Customer fields or a defined subset? Without a field list, a completeness assertion cannot be made.

4. **AMB-4 — National identifier comparison behaviour (AC-7):** The criterion states national identifier is used "when provided on both records being compared." If only one of the two records has a national identifier, is that field excluded from the comparison (treated as absent), or does the system treat the missing value on one side as a non-match? This distinction affects boundary test design.

5. **AMB-5 — Status of the Pending record after a merge where the Pending record is the non-survivor (AC-5):** If the Supervisor designates the existing record as survivor and the new Pending record as non-survivor, does the Pending record transition directly from Pending to Merged? BR-016's transition matrix does not include `Pending → Merged` as a permitted transition. This may be a gap in the status transition matrix or an implied permitted transition specific to the merge workflow.

6. **AMB-6 — "Before the record is saved" (AC-1):** The criterion states duplicate detection runs "before the record is saved." Does this mean the record is not persisted at all until detection completes without a match, or is the record saved as Pending immediately and detection runs as part of the save transaction? The distinction affects whether a system error during detection leaves a persisted Pending record or no record.

7. **AMB-7 — Written reason storage for dismissal (AC-4):** Where is the Supervisor's written dismissal reason stored? The data model does not define a dismissal reason field on the Customer entity, the Customer Status History entity (which has an optional `notes` field), or a separate dismissal record. This affects data-state tests for dismissal audit content.

8. **AMB-8 — "All other activation requirements" (AC-4):** AC-4 states the record "becomes eligible to transition to Active, subject to all other activation requirements being met." This implies a set of requirements beyond the Duplicate Flag. Are these requirements the standard Pending → Active preconditions (at least one verified contact method per BR-023)? Or are there additional requirements specific to this workflow?

---

## Conflicts and Risks

1. **Potential Gap — Pending → Merged not in transition matrix:** AC-5 implies the new Pending record may be designated the non-survivor and transition to Merged status. The permitted transition matrix in BR-016 does not include `Pending → Merged` as an allowed transition. If this transition is required by the merge workflow, it either represents an implicit permitted transition not documented in BR-016, or a gap in the business rules. **Source:** AC-5 requirement text ("set the non-survivor record to Merged status") vs. BR-016 (transition matrix lists only: Pending→Active, Pending→Closed, Active→Suspended, Active→Closed, Suspended→Active, Suspended→Closed). **Nature:** The requirement implies a status transition (Pending → Merged) that does not appear in the BR-016 permitted transition matrix. This is not necessarily a direct contradiction — merge transitions may be governed separately from the standard status transition rules — but the omission is a risk that requires confirmation.

2. **No conflict detected between the requirement and known limitations** beyond what is already captured as ambiguities and constraints. The requirement's explicit statement that "update-triggered detection (BR-012) is out of scope for this story" is consistent with the knowledge base.

3. **No internal contradictions within the requirement itself** were detected beyond the Pending → Merged transition issue above.

---

## Recommended Test Areas

| Test Area | Applicable | Reason |
|---|---|---|
| Positive | Yes | Happy-path creation with no matching records: record is created, no flag raised, Agent can proceed to activate (subject to BR-023). |
| Negative | Yes | Creation with matching records triggers flag; Agent attempts to dismiss/merge and is rejected; Agent attempts Pending→Active with open flag and is rejected; dismissal without written reason is rejected. |
| Boundary | Yes | AC-7 specifies five matching fields including national identifier with "when provided" conditionality; boundary tests apply to field-level matching thresholds (constrained by LIM-031) and field length limits on first_name (1, 100, 101 chars), last_name (1, 150, 151 chars), national_identifier (4, 5, 20, 21 chars), and email_address (254, 255 chars). |
| Permission | Yes | Agent cannot dismiss flag or initiate merge (AC-6); Agent cannot transition Pending→Active with open flag (AC-8); Supervisor can dismiss (AC-4) and initiate merge (AC-5); Viewer cannot perform any write action in this workflow; restricted field (national identifier) visible to Supervisor but not Agent in comparison view (BR-039). |
| Lifecycle | Yes | Pending→Active blocked while flag open (AC-8); Pending→Active permitted after flag dismissed (AC-4); non-survivor transitions to Merged after merge (AC-5); Pending→Merged not in BR-016 matrix (potential gap — see Conflicts). |
| Integration | Yes | AC-5 explicitly requires all downstream systems to be notified on merge completion (BR-037, LIM-024, LIM-030). |
| Data Validation | Yes | Duplicate detection matching fields (first name, last name, primary email, primary phone, national identifier) have data model constraints; email format (RFC 5321), phone format (E.164), national identifier format (5–20 chars, country-specific), name whitespace and length rules all require validation. |
| Concurrency | Yes | BR-036 and LIM-028 establish that concurrent merge operations on the same record are serialised; a second merge attempt on a record already in-progress must return a conflict error. |
| Audit | Yes | Flag creation, flag dismissal, and merge operations must all produce audit entries per BR-043; the content and immutability of those entries must be verifiable. |

---

## Risk Classification

**Level:** High

The requirement governs the primary data integrity gate that prevents duplicate Active customer records from entering the system — a failure in this flow has direct, serious consequences for billing, communications, and regulatory compliance. Multiple intersecting business rules (BR-004, BR-006, BR-011, BR-014, BR-015, BR-016, BR-032, BR-033, BR-035, BR-037, BR-038, BR-043) must all function correctly together. The requirement involves an irreversible operation (merge), lifecycle state transitions, downstream system integration events delivered asynchronously, restricted field handling (national identifier), and a potential gap in the BR-016 status transition matrix (Pending → Merged not listed). Several acceptance criteria are Partially Testable due to unspecified field display requirements (AC-3), unresolved survivor designation constraints (AC-5), and environment-specific threshold configuration (AC-7, LIM-031). The combination of lifecycle, permission, integration, and concurrency test areas across an irreversible operation warrants a High risk classification; it does not reach Critical because no conflict with a business rule is confirmed (only a potential gap) and no compliance-specific data (consent records) is at the centre of the workflow.

---

## Assumptions

| # | Assumption | Type | Source |
|---|---|---|---|
| A-1 | The Duplicate Flag referred to throughout the requirement is the flag described in BR-011 and BR-014/BR-015, raised automatically by the system at creation time. | Knowledge-Based | business-rules.md BR-011, BR-014, BR-015; glossary.md — Duplicate Flag |
| A-2 | Duplicate detection runs as part of the record creation transaction (at save time), before the record is persisted as Pending, based on AC-1's phrase "before the record is saved" and BR-011's description of detection "at the point of creation." | Knowledge-Based | business-rules.md BR-011; AC-1 |
| A-3 | The five fields listed in AC-7 (first name, last name, primary email, primary phone, national identifier) are the specific fields from the "configurable matching algorithm (name similarity, email, phone, national identifier)" described in BR-011. | Knowledge-Based | business-rules.md BR-011 |
| A-4 | Secondary email addresses and secondary phone numbers are excluded from duplicate detection input per the requirement's Notes section, which is consistent with LIM-008. | Knowledge-Based | known-limitations.md LIM-008; requirement Notes section |
| A-5 | The written dismissal reason required by AC-4 and BR-014 is stored in the `notes` field of the Customer Status History entity or an equivalent audit record, as the data model does not define a dedicated dismissal reason field. | Unverified | None |
| A-6 | The Pending → Merged status transition required for a non-survivor Pending record (AC-5) is an implicit exception to the BR-016 matrix, applicable only within the merge workflow, and is not a defect in the business rules document. | Unverified | None |
| A-7 | "All other activation requirements" in AC-4 refers to the standard Pending → Active preconditions: at least one verified contact method (BR-023) and passage of duplicate detection without a remaining open flag. | Knowledge-Based | business-rules.md BR-023, BR-004, BR-015 |
| A-8 | The comparison view described in AC-3 is the "Duplicate Management" functional area described in application-context.md Section 7. | Knowledge-Based | application-context.md Section 7 |
| A-9 | Audit events are generated for: (a) Duplicate Flag creation, (b) Duplicate Flag dismissal, (c) merge initiation, and (d) merge completion, per BR-043's requirement that all status changes and merges produce audit entries. | Knowledge-Based | business-rules.md BR-043 |
| A-10 | [INFERRED] The Duplicate Flag is a boolean or status indicator on the Customer record or a related flag entity, not a separate workflow task object — this is inferred from the glossary definition of Duplicate Flag and BR-011/BR-015, but the data model does not define its physical representation. | Unverified | None |

---

## Questions for Product Owner

1. **Q-1 — Duplicate Flag data representation (AMB-1):** The data model does not define where the Duplicate Flag is stored (no flag field on the Customer entity, no Duplicate Flag entity in data-model.md). What entity or field represents the Duplicate Flag, and what are its allowed states (e.g., Open, Dismissed, Resolved via Merge)? *(blocking_for_specific_tests: true; affected test areas: Data Validation, Audit, Lifecycle; affected criteria: AC-2, AC-4, AC-5, AC-8)*

2. **Q-2 — Survivor designation constraints (AMB-2, AC-5):** When a Supervisor initiates a merge from a Pending record flagged as a duplicate of an existing Active record, is there a rule governing which record must be the survivor? Can the Supervisor designate the new Pending record as the survivor (retiring the existing Active record), or must the existing Active record always be the survivor? *(blocking_for_specific_tests: true; affected test areas: Lifecycle, Permission, Positive; affected criteria: AC-5)*

3. **Q-3 — Comparison view field list (AMB-3, AC-3):** What specific fields must the system display in the comparison view when a Supervisor opens a flagged record (AC-3)? Should the national identifier be shown (it is a restricted field visible to Supervisors per BR-039), and is there a defined minimum field set? *(blocking_for_specific_tests: true; affected test areas: Positive, Permission; affected criteria: AC-3)*

4. **Q-4 — National identifier comparison logic (AMB-4, AC-7):** When only one of the two records being compared has a national identifier, what should happen? (a) Skip national identifier comparison for that pair and use the other four fields only, or (b) treat the missing value as a non-match, reducing the overall similarity score? *(blocking_for_specific_tests: true; affected test areas: Boundary, Data Validation; affected criteria: AC-7)*

5. **Q-5 — Pending → Merged transition validity (Conflict item 1):** The BR-016 permitted transition matrix does not include `Pending → Merged`. If a Pending record is the non-survivor in a merge, must it first transition to Active before being merged, or is `Pending → Merged` an implicit permitted transition within the merge workflow that is simply missing from the matrix documentation? *(blocking_for_specific_tests: true; affected test areas: Lifecycle; affected criteria: AC-5)*

6. **Q-6 — Dismissal reason storage (AMB-7, AC-4):** Where is the Supervisor's written dismissal reason stored? Is it captured in the `notes` field of the Customer Status History record, attached to the (undefined) Duplicate Flag record, or stored elsewhere? This affects data-state and audit assertions for AC-4. *(blocking_for_specific_tests: true; affected test areas: Audit, Data Validation; affected criteria: AC-4)*

7. **Q-7 — Duplicate detection threshold configuration for testing (LIM-031):** What matching threshold values should be configured in the test environment for deterministic duplicate detection test execution? Specifically, what similarity score triggers a flag for name fields, and what weight is applied to each of the five AC-7 fields? *(blocking_for_specific_tests: true; affected test areas: Boundary, Data Validation; affected criteria: AC-7)*

8. **Q-8 — Record creation behaviour when detection returns no matches (AC-1):** The Notes section states "if no matching records are found, the system must not block creation." Does the record then proceed directly to Pending status without any flag, and can the Agent immediately attempt Pending → Active? Or is there any additional review step for unmatched records? *(blocking_for_specific_tests: false; blocking_for_entire_suite: false; affected test areas: Positive; affected criteria: AC-1)*

9. **Q-9 — "Before the record is saved" interpretation (AMB-6):** Does AC-1's phrase "before the record is saved" mean detection runs before any record is persisted (so a detection failure leaves no record in the system), or after the record is persisted as Pending but before it can be activated? *(blocking_for_specific_tests: true; affected test areas: Negative, Lifecycle; affected criteria: AC-1, AC-2)*

---

## Handoff Package

```yaml
handoff:
  schema_version: "1.1"
  requirement_id: "US-042"
  risk_level: "High"
  ready_for_test_generation: true
  blocker_reason: null

  readiness:
    suite_blockers: []
    expected_generation_mix:
      ready: >
        AC-1 (creation triggers detection — exact match scenarios),
        AC-2 (flag raised, status remains Pending),
        AC-4 (Supervisor dismissal with written reason — flag cleared, record eligible for Active),
        AC-6 (Agent rejection for dismiss and merge attempts — error message returned),
        AC-8 (Agent rejection for Pending→Active with open flag — error message returned);
        permission boundary tests for all five roles across all AC actions;
        lifecycle tests for Pending→Active blocked/permitted transitions;
        audit event generation for flag creation, dismissal, merge initiation, and completion.
      constrained: >
        AC-3 (comparison view content — field list unspecified; generate tests for Supervisor access
        to the view and presence of non-restricted fields, mark field-completeness assertions
        CONSTRAINED pending Q-3);
        AC-5 (merge completion — downstream notification delivery testable via stub per LIM-030;
        survivor designation assertions CONSTRAINED pending Q-2; Pending→Merged transition
        CONSTRAINED pending Q-5 confirmation);
        AC-7 (exact-match duplicate detection tests for each of the five specified fields are
        testable; near-match boundary tests CONSTRAINED citing LIM-031 — must document threshold
        configuration precondition; national identifier one-sided match behaviour CONSTRAINED
        pending Q-4);
        secondary contact method non-detection tests (LIM-008 — confirm secondary email/phone
        does not trigger flag).
      blocked: >
        Duplicate Flag data-state tests (flag field identity, flag state values, flag cleared state)
        BLOCKED pending Q-1;
        Dismissal reason data-state and audit content tests BLOCKED pending Q-6;
        Duplicate detection threshold boundary precision tests BLOCKED pending Q-7;
        AC-1 negative path for detection system error BLOCKED pending Q-9 interpretation.

  summary:
    business_objective: >
      Maintain a single, accurate, deduplicated customer record as the organisation's source
      of truth by preventing potentially duplicate records from reaching Active status without
      authorised Supervisor review.
    feature_areas:
      - "Customer record management"
      - "Duplicate detection"
      - "Customer merge"
      - "Account status management"
      - "Activity and audit history"

  actors:
    - actor: "Customer Service Agent"
      role: "Agent"
    - actor: "Supervisor"
      role: "Supervisor"
    - actor: "System (duplicate detection engine)"
      role: "System"

  impacted_rules:
    - id: "BR-001"
      title: "Mandatory Fields on Creation"
      relationship: "Exercised"
    - id: "BR-003"
      title: "Agent Role Required for Creation"
      relationship: "Exercised"
    - id: "BR-004"
      title: "Duplicate Check Before Activation"
      relationship: "Exercised"
    - id: "BR-005"
      title: "System-Generated Customer ID"
      relationship: "Exercised"
    - id: "BR-006"
      title: "Initial Status is Pending"
      relationship: "Exercised"
    - id: "BR-008"
      title: "National ID Field Restricted"
      relationship: "Constrained by"
    - id: "BR-009"
      title: "One Record Per Verified Identity"
      relationship: "Exercised"
    - id: "BR-011"
      title: "Automatic Duplicate Flagging"
      relationship: "Exercised"
    - id: "BR-014"
      title: "Duplicate Dismissal Requires Authorization"
      relationship: "Exercised"
    - id: "BR-015"
      title: "Duplicate Flag Blocks Activation"
      relationship: "Exercised"
    - id: "BR-016"
      title: "Allowed Status Transitions"
      relationship: "Exercised"
    - id: "BR-022"
      title: "Status Change Propagated to Downstream"
      relationship: "Exercised"
    - id: "BR-032"
      title: "Merge Requires Supervisor Authorization"
      relationship: "Exercised"
    - id: "BR-033"
      title: "Merge Designates One Survivor"
      relationship: "Exercised"
    - id: "BR-034"
      title: "Merge is Irreversible"
      relationship: "Exercised"
    - id: "BR-035"
      title: "Non-Survivor Retained for Audit"
      relationship: "Exercised"
    - id: "BR-036"
      title: "Only One Active Merge Per Record"
      relationship: "Constrained by"
    - id: "BR-037"
      title: "Downstream Systems Notified on Merge"
      relationship: "Exercised"
    - id: "BR-038"
      title: "Role-Based Access Enforcement"
      relationship: "Exercised"
    - id: "BR-039"
      title: "Restricted Fields Require Elevated Role"
      relationship: "Constrained by"
    - id: "BR-043"
      title: "All Changes Produce Audit Entries"
      relationship: "Exercised"
    - id: "BR-051"
      title: "Validation Errors Returned with Field-Level Detail"
      relationship: "Exercised"
    - id: "BR-052"
      title: "Rejected Transitions Return Business Reason"
      relationship: "Exercised"
    - id: "BR-056"
      title: "Duplicate Resolution Rate is a Tracked Metric"
      relationship: "Constrained by"

  impacted_entities:
    - entity: "Customer"
      fields:
        - name: "customer_id"
          operation: "Create"
          constraint: "System-generated UUID; immutable; globally unique — BR-005, BR-007"
        - name: "customer_type"
          operation: "Create"
          constraint: "Individual or Organisation; mandatory; immutable after creation — LIM-002"
        - name: "first_name"
          operation: "Create"
          constraint: "1–100 chars; not whitespace-only; used as AC-7 duplicate detection input — BR-048"
        - name: "last_name"
          operation: "Create"
          constraint: "1–150 chars; not whitespace-only; used as AC-7 duplicate detection input — BR-048"
        - name: "national_identifier"
          operation: "Validate"
          constraint: "Optional; 5–20 alphanumeric chars; restricted field (Supervisor+ only); AC-7 detection input when present on both records — BR-008, BR-039"
        - name: "status"
          operation: "Validate"
          constraint: "Must remain Pending while Duplicate Flag open (BR-015); Pending→Active blocked; non-survivor transitions to Merged (BR-016 gap — see Q-5)"
        - name: "created_by"
          operation: "Create"
          constraint: "Must reference a valid User with Agent role or above — BR-003"
        - name: "merged_into"
          operation: "Update"
          constraint: "Required when status = Merged; must reference the surviving customer — BR-010, BR-035"
    - entity: "Email"
      fields:
        - name: "email_address"
          operation: "Validate"
          constraint: "RFC 5321; max 254 chars; unique across Active and Pending for Primary type; AC-7 detection input — BR-002, BR-024"
        - name: "email_type"
          operation: "Validate"
          constraint: "Uniqueness and duplicate detection apply to Primary only — LIM-008"
        - name: "is_verified"
          operation: "Validate"
          constraint: "Must be true (with verified_at) for Pending→Active transition — BR-023"
    - entity: "Phone"
      fields:
        - name: "phone_number"
          operation: "Validate"
          constraint: "E.164 format; max 15 digits; unique across Active and Pending for Primary type; AC-7 detection input — BR-025, BR-026"
        - name: "phone_type"
          operation: "Validate"
          constraint: "Uniqueness and duplicate detection apply to Primary only — LIM-008"
    - entity: "Merge History"
      fields:
        - name: "survivor_customer_id"
          operation: "Create"
          constraint: "Must reference an Active Customer after merge; distinct from non_survivor_customer_id"
        - name: "non_survivor_customer_id"
          operation: "Create"
          constraint: "Transitions to Merged; can be non-survivor in at most one Merge History record — BR-036"
        - name: "initiated_by"
          operation: "Create"
          constraint: "Must reference a User with Supervisor role or above — BR-032"
        - name: "confirmed_by"
          operation: "Create"
          constraint: "Must reference a User with Supervisor role or above — BR-032"
    - entity: "Customer Status History"
      fields:
        - name: "new_status"
          operation: "Create"
          constraint: "Must be a permitted transition per BR-016; Pending→Merged not listed (Q-5)"
        - name: "changed_by"
          operation: "Create"
          constraint: "Must reference a valid User or system identity"
    - entity: "Audit Event"
      fields:
        - name: "action"
          operation: "Create"
          constraint: "CREATE, STATUS_CHANGE, MERGE applicable — BR-043"
        - name: "performed_by"
          operation: "Create"
          constraint: "Must reference the acting User or system identity"

  relevant_limitations:
    - id: "LIM-004"
      title: "No Bulk Customer Creation"
      testing_impact: "All test scenarios must use individual record creation; batch creation is not a valid test path."
    - id: "LIM-008"
      title: "Secondary Contact Methods Are Not Deduplicated"
      testing_impact: "Duplicate detection tests must use primary email/phone only; secondary contact duplicates must not trigger a flag."
    - id: "LIM-015"
      title: "Merge Cannot Be Partially Reversed"
      testing_impact: "Tests must confirm no merge reversal option exists; non-survivor remains in Merged status permanently."
    - id: "LIM-016"
      title: "Merge Does Not Automatically Resolve Data Conflicts"
      testing_impact: "AC-5 merge tests must not assert automatic field selection; Supervisor must be presented with both records' values."
    - id: "LIM-017"
      title: "Only Two Records Can Be Merged in a Single Operation"
      testing_impact: "Merge tests are scoped to exactly two records; three-record merge submission must be tested as a rejection scenario."
    - id: "LIM-024"
      title: "Downstream Systems Are Notified Asynchronously"
      testing_impact: "AC-5 integration tests must account for asynchronous delivery; immediate downstream state assertions are invalid."
    - id: "LIM-030"
      title: "Test Environments Do Not Receive Live Downstream Events"
      testing_impact: "AC-5 downstream notification tests must use stub/mock systems and event-listening verification."
    - id: "LIM-031"
      title: "Duplicate Detection Sensitivity Is Configurable and Environment-Specific"
      testing_impact: "Duplicate detection tests must verify threshold configuration preconditions before asserting flag behaviour; near-match boundary tests are constrained."

  test_areas:
    - area: "Positive"
      applicable: true
      reason: "Happy-path creation with no matching records produces no flag; Agent can proceed to activate after standard preconditions are met."
    - area: "Negative"
      applicable: true
      reason: "Creation with matching records triggers flag; Agent dismiss/merge rejected with error message; Agent Pending→Active rejected; dismissal without reason rejected."
    - area: "Boundary"
      applicable: true
      reason: "AC-7 five-field detection inputs have data model length/format boundaries; near-match thresholds are configurable (CONSTRAINED by LIM-031)."
    - area: "Permission"
      applicable: true
      reason: "Agent cannot dismiss or merge (AC-6); Agent cannot activate with open flag (AC-8); Supervisor can dismiss (AC-4) and merge (AC-5); national identifier restricted from Agent view in comparison (BR-039)."
    - area: "Lifecycle"
      applicable: true
      reason: "Pending→Active blocked while flag open (AC-8); Pending→Active permitted after dismissal (AC-4); non-survivor transitions to Merged (AC-5); Pending→Merged not in BR-016 matrix (Q-5)."
    - area: "Integration"
      applicable: true
      reason: "AC-5 explicitly requires downstream system notification on merge completion via asynchronous event (BR-037, LIM-024, LIM-030)."
    - area: "Data Validation"
      applicable: true
      reason: "Detection input fields (first name, last name, primary email, primary phone, national identifier) each have format, length, and uniqueness constraints from the data model."
    - area: "Concurrency"
      applicable: true
      reason: "BR-036 and LIM-028 require that concurrent merge attempts on the same record are serialised; second attempt must return a conflict error."
    - area: "Audit"
      applicable: true
      reason: "Flag creation, dismissal, merge initiation, and merge completion must each produce audit entries per BR-043; content and immutability must be verifiable."

  acceptance_criteria:
    - id: "AC-1"
      text: "Given I am a logged-in Agent, when I submit a new customer creation request, then the system must automatically run duplicate detection against all Active and Pending customer records before the record is saved."
      classification: "Testable"
      missing_information: null
    - id: "AC-2"
      text: "Given duplicate detection identifies one or more potential matches, when the new customer record is created, then the system must raise a Duplicate Flag on the new record and retain its status as Pending."
      classification: "Testable"
      missing_information: null
    - id: "AC-3"
      text: "Given a Duplicate Flag exists on a Pending record, when a Supervisor opens the flagged record, then the system must display the list of matching records alongside the flagged record to support comparison and review."
      classification: "Partially Testable"
      missing_information: "The specific fields required in the comparison view are not defined; national identifier display to Supervisor is unspecified; field completeness assertions cannot be written without a defined field list (Q-3)."
    - id: "AC-4"
      text: "Given a Duplicate Flag is open on a Pending record, when a Supervisor dismisses the flag and provides a written reason, then the flag is cleared and the record becomes eligible to transition to Active, subject to all other activation requirements being met."
      classification: "Testable"
      missing_information: null
    - id: "AC-5"
      text: "Given a Duplicate Flag is open on a Pending record, when a Supervisor initiates a merge and designates the survivor record, then the system must complete the merge, set the non-survivor record to Merged status, link the non-survivor to the survivor, and notify all downstream systems."
      classification: "Partially Testable"
      missing_information: "Survivor designation constraints are unspecified — whether the Pending record can be the survivor is unclear (Q-2). Pending→Merged transition is absent from BR-016 matrix (Q-5). Downstream notification event schema is governed by fixed integration contracts not detailed in the requirement (LIM-026)."
    - id: "AC-6"
      text: "Given a Duplicate Flag is open on a Pending record, when an Agent attempts to dismiss the flag or initiate a merge, then the system must reject the action and return a clear error message indicating that Supervisor authorisation is required."
      classification: "Testable"
      missing_information: null
    - id: "AC-7"
      text: "The duplicate detection algorithm must evaluate the following fields when comparing a new record against existing records: first name, last name, primary email address, primary phone number, and national identifier (when provided on both records being compared)."
      classification: "Partially Testable"
      missing_information: "Matching thresholds and field weights are configurable and environment-specific (LIM-031); near-match boundary tests cannot assert deterministic outcomes without threshold documentation (Q-7). Behaviour when national identifier is present on only one record is unspecified (Q-4)."
    - id: "AC-8"
      text: "Given a Pending record has an open Duplicate Flag, when an Agent attempts to transition the record to Active, then the system must reject the transition and return a message stating that an open Duplicate Flag must be resolved before activation."
      classification: "Testable"
      missing_information: null

  boundary_conditions:
    - field: "first_name"
      entity: "Customer"
      condition: "Empty string or whitespace only → Rejected (BR-048); exactly 100 chars → Accepted; 101 chars → Rejected"
    - field: "last_name"
      entity: "Customer"
      condition: "Empty string or whitespace only → Rejected (BR-048); exactly 150 chars → Accepted; 151 chars → Rejected (implied by 1–150 constraint)"
    - field: "national_identifier"
      entity: "Customer"
      condition: "4 chars → Rejected (minimum 5); 5 chars → Accepted; 20 chars → Accepted; 21 chars → Rejected (maximum 20)"
    - field: "email_address"
      entity: "Email"
      condition: "Missing @ → Rejected; 254 chars → Accepted; 255 chars → Rejected; uppercase → Accepted (normalised to lowercase)"
    - field: "phone_number"
      entity: "Phone"
      condition: "Without + country prefix → Rejected or normalised; fewer than 7 digits after country code → Rejected; more than 15 digits → Rejected"
    - field: "status"
      entity: "Customer"
      condition: "Any transition not in BR-016 matrix (including Pending→Merged if unconfirmed by Q-5) → Rejected with business reason"

  invalid_combinations:
    - description: "status = Active with an open Duplicate Flag"
      relevant_because: "BR-015 blocks this transition; this combination must be impossible to reach."
    - description: "Agent role user + dismiss Duplicate Flag action"
      relevant_because: "BR-014 and BR-038 require Supervisor authorisation; Agent performing dismissal must be rejected."
    - description: "Agent role user + initiate merge action"
      relevant_because: "BR-032 and BR-038 require Supervisor authorisation; Agent performing merge must be rejected."
    - description: "status = Merged with merged_into = null"
      relevant_because: "BR-010 and BR-035 require the non-survivor to reference the survivor; null merged_into on a Merged record is invalid."
    - description: "Merge History where non_survivor_customer_id already has a Merge History entry"
      relevant_because: "BR-036 prohibits merging a record that has already been merged once."
    - description: "email_type = Secondary used as duplicate detection input"
      relevant_because: "LIM-008 excludes secondary contact methods from deduplication; system must not flag on secondary email match."
    - description: "Merge operation with survivor_customer_id = non_survivor_customer_id"
      relevant_because: "Merge History unique constraint prohibits self-merge; this must be rejected."

  open_questions:
    - id: "Q-1"
      question: "The data model does not define a Duplicate Flag entity or field on the Customer entity. What entity or field represents the Duplicate Flag, and what are its allowed states (e.g., Open, Dismissed, Resolved via Merge)?"
      blocking_for_specific_tests: true
      blocking_for_entire_suite: false
      affected_acceptance_criteria: ["AC-2", "AC-4", "AC-5", "AC-8"]
      affected_test_areas: ["Data Validation", "Audit", "Lifecycle"]
      blocking: true
      affects_ready: false
    - id: "Q-2"
      question: "When a Supervisor initiates a merge from a Pending record flagged as a duplicate of an existing Active record, can either record be designated the survivor, or must the existing Active record always be the survivor?"
      blocking_for_specific_tests: true
      blocking_for_entire_suite: false
      affected_acceptance_criteria: ["AC-5"]
      affected_test_areas: ["Lifecycle", "Permission", "Positive"]
      blocking: true
      affects_ready: false
    - id: "Q-3"
      question: "What specific fields must the system display in the comparison view when a Supervisor opens a flagged record (AC-3)? Should the national identifier be included, and is there a defined minimum field set?"
      blocking_for_specific_tests: true
      blocking_for_entire_suite: false
      affected_acceptance_criteria: ["AC-3"]
      affected_test_areas: ["Positive", "Permission"]
      blocking: true
      affects_ready: false
    - id: "Q-4"
      question: "When only one of the two records being compared has a national identifier, should the system skip national identifier comparison for that pair, or treat the missing value as a non-match that reduces the similarity score?"
      blocking_for_specific_tests: true
      blocking_for_entire_suite: false
      affected_acceptance_criteria: ["AC-7"]
      affected_test_areas: ["Boundary", "Data Validation"]
      blocking: true
      affects_ready: false
    - id: "Q-5"
      question: "The BR-016 permitted transition matrix does not include Pending → Merged. If a Pending record is the non-survivor in a merge, does it transition directly from Pending to Merged, and if so, is this an implicit permitted transition within the merge workflow that is missing from the BR-016 documentation?"
      blocking_for_specific_tests: true
      blocking_for_entire_suite: false
      affected_acceptance_criteria: ["AC-5"]
      affected_test_areas: ["Lifecycle"]
      blocking: true
      affects_ready: false
    - id: "Q-6"
      question: "Where is the Supervisor's written dismissal reason stored — in the notes field of the Customer Status History record, attached to the Duplicate Flag record (if it is a separate entity), or elsewhere?"
      blocking_for_specific_tests: true
      blocking_for_entire_suite: false
      affected_acceptance_criteria: ["AC-4"]
      affected_test_areas: ["Audit", "Data Validation"]
      blocking: true
      affects_ready: false
    - id: "Q-7"
      question: "What matching threshold values (similarity score, field weights) should be configured in the test environment for deterministic duplicate detection test execution against each of the five AC-7 fields?"
      blocking_for_specific_tests: true
      blocking_for_entire_suite: false
      affected_acceptance_criteria: ["AC-7"]
      affected_test_areas: ["Boundary", "Data Validation"]
      blocking: true
      affects_ready: false
    - id: "Q-8"
      question: "When no matching records are found during duplicate detection, does the record proceed directly to Pending status with no further review step, allowing the Agent to immediately attempt Pending → Active?"
      blocking_for_specific_tests: false
      blocking_for_entire_suite: false
      affected_acceptance_criteria: ["AC-1"]
      affected_test_areas: ["Positive"]
      blocking: false
      affects_ready: false
    - id: "Q-9"
      question: "Does AC-1's phrase 'before the record is saved' mean detection runs before any record is persisted (no record exists in the system if detection errors), or after the record is persisted as Pending but before it can be activated?"
      blocking_for_specific_tests: true
      blocking_for_entire_suite: false
      affected_acceptance_criteria: ["AC-1", "AC-2"]
      affected_test_areas: ["Negative", "Lifecycle"]
      blocking: true
      affects_ready: false

  conflicts:
    - requirement_text: "set the non-survivor record to Merged status"
      conflicts_with: "BR-016"
      nature: "The BR-016 permitted transition matrix does not include Pending → Merged as an allowed transition; if the non-survivor is a Pending record, this transition has no defined authorisation in the rules."
      severity: "High"

  assumptions:
    - text: "The Duplicate Flag referred to throughout the requirement is the flag described in BR-011 and BR-014/BR-015, raised automatically by the system at creation time."
      type: "Knowledge-Based"
      source: "business-rules.md BR-011, BR-014, BR-015; glossary.md — Duplicate Flag"
      confidence: "CERTAIN"
    - text: "Duplicate detection runs as part of the record creation transaction (at save time), before the record is persisted as Pending, based on AC-1's phrase 'before the record is saved' and BR-011's description of detection 'at the point of creation.'"
      type: "Knowledge-Based"
      source: "business-rules.md BR-011; AC-1 requirement text"
      confidence: "INFERRED"
    - text: "The five fields listed in AC-7 are the specific fields from the configurable matching algorithm described in BR-011 (name similarity, email, phone, national identifier)."
      type: "Knowledge-Based"
      source: "business-rules.md BR-011"
      confidence: "INFERRED"
    - text: "Secondary email addresses and secondary phone numbers are excluded from duplicate detection input, consistent with LIM-008 and the requirement's Notes section."
      type: "Knowledge-Based"
      source: "known-limitations.md LIM-008; requirement Notes section"
      confidence: "CERTAIN"
    - text: "The written dismissal reason required by AC-4 and BR-014 is stored in the notes field of the Customer Status History entity or an equivalent audit record, as the data model does not define a dedicated dismissal reason field."
      type: "Unverified"
      source: null
      confidence: "UNCERTAIN"
    - text: "The Pending → Merged status transition required for a non-survivor Pending record (AC-5) is an implicit exception to the BR-016 matrix, applicable only within the merge workflow, and is not a defect in the business rules document."
      type: "Unverified"
      source: null
      confidence: "UNCERTAIN"
    - text: "'All other activation requirements' in AC-4 refers to the standard Pending → Active preconditions: at least one verified contact method (BR-023) and no remaining open duplicate flag (BR-015)."
      type: "Knowledge-Based"
      source: "business-rules.md BR-023, BR-004, BR-015"
      confidence: "INFERRED"
    - text: "The comparison view described in AC-3 corresponds to the Duplicate Management functional area described in application-context.md Section 7."
      type: "Knowledge-Based"
      source: "application-context.md Section 7"
      confidence: "INFERRED"
    - text: "Audit events are generated for Duplicate Flag creation, dismissal, merge initiation, and merge completion, per BR-043's requirement that all status changes and merges produce audit entries."
      type: "Knowledge-Based"
      source: "business-rules.md BR-043"
      confidence: "CERTAIN"
    - text: "The Duplicate Flag is a boolean or status indicator on the Customer record or a related flag entity — this is inferred from the glossary definition and BR-011/BR-015 but the data model does not define its physical representation."
      type: "Unverified"
      source: null
      confidence: "UNCERTAIN"
```

---

### Pre-Delivery Validation Checklist

| Check | Status |
|---|---|
| V-01: All BR-IDs exist in business-rules.md | ✅ All 24 cited rules verified against the index |
| V-02: All LIM-IDs exist in known-limitations.md | ✅ All 8 cited limitations verified against the index |
| V-03: All entities and fields exist in data-model.md | ✅ Customer, Email, Phone, Merge History, Customer Status History, Audit Event all verified |
| V-04: All actors mapped to defined roles | ✅ Agent, Supervisor, System — all mapped |
| V-05: Risk level consistent with criteria | ✅ High — multiple business rules implicated, lifecycle transitions, irreversible operation, integration; no confirmed Critical conflict with primary success condition |
| V-06: No invented business rules, invented ACs, or generated test cases | ✅ All rules cited by BR-ID; no ACs invented; no test steps generated |
| V-07: All ambiguities phrased as specific, answerable questions | ✅ AMB-1 through AMB-8 are each specific and answerable |
| V-08: All conflicts cite requirement text and knowledge source reference | ✅ One conflict documented with requirement text and BR-016 reference |
| V-09: Handoff Package contains all required fields | ✅ All schema 1.1 required fields present |
| V-10: Known limitations described as testing constraints, not defects | ✅ All limitations framed as scope boundaries |
| V-11: All 15 required output sections present | ✅ All sections present |
| V-12: Knowledge-Based assumptions include citations; Unverified assumptions have no fabricated citations | ✅ A-5, A-6, A-10 (Unverified) have null source |
| V-13: Every material open question has at least one blocking flag set to true | ✅ Q-1 through Q-7 and Q-9 have blocking_for_specific_tests: true; Q-8 is non-material (confirmatory) |
| V-14: ready_for_test_generation: true → no question has blocking_for_entire_suite: true | ✅ No question has blocking_for_entire_suite: true |
| V-15: ready_for_test_generation: true → blocker_reason is null | ✅ blocker_reason: null |
| V-16: Questions with blocking_for_specific_tests: true list affected_acceptance_criteria or affected_test_areas | ✅ All blocking questions include both fields where determinable |