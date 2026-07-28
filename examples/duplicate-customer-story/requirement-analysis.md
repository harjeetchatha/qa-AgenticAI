# Requirement Analysis

**Requirement ID:** US-042
**Requirement Source:** knowledge/requirements/duplicate-customer-story.md
**Analysis Date:** 2026-07-24
**Risk Level:** High

---

## Requirement Summary

When a Customer Service Agent creates a new customer record, the system must automatically run duplicate detection against all Active and Pending records before saving. If one or more potential matches are found, the system raises a Duplicate Flag and holds the new record in Pending status. The record cannot be activated while the flag is open. A Supervisor must then review the flagged record alongside the matching records and take one of two resolution actions: dismiss the flag with a written reason (making the record eligible for activation), or initiate a merge designating which record survives. An Agent has no authority to dismiss the flag or initiate a merge — any such attempt must be explicitly rejected. The duplicate detection algorithm matches on first name, last name, primary email, primary phone, and national identifier (where provided on both records). Secondary contact methods and update-triggered detection are explicitly out of scope for this story.

---

## Business Objective

Prevent duplicate Active customer records from entering the system by gating activation on automated duplicate detection and Supervisor-authorised resolution, preserving the organisation's customer master data as a single, accurate source of truth. *(application-context.md Section 11 — Data integrity)*

---

## Actors and Roles

| Actor | Mapped Role | Source |
|---|---|---|
| Customer Service Agent | Agent | glossary.md — Agent (Role); application-context.md Section 3 |
| Supervisor | Supervisor | glossary.md — Supervisor (Role); application-context.md Section 3 |
| System (duplicate detection engine) | System | application-context.md Section 4; BR-011 |

No unmapped actors identified.

---

## Impacted Features

- **Duplicate detection** — Core mechanism; detection runs automatically at creation (application-context.md Section 5)
- **Customer record management** — New record is created, saved in Pending, and ultimately activated or merged (application-context.md Section 5)
- **Customer merge** — Supervisor-initiated merge is one resolution path (application-context.md Section 5)
- **Account status management** — Pending → Active transition is gated; Pending → Merged occurs as merge outcome (application-context.md Section 5)
- **Activity and audit history** — All actions (flag creation, dismissal, merge) must be logged immutably (application-context.md Section 5)

---

## Impacted Business Rules

| Rule ID | Title | Relevance | Relationship |
|---|---|---|---|
| BR-002 | Unique Email on Creation | Primary email is a matching field; a duplicate primary email triggers a flag and blocks creation of an Active record with the same address | Exercised |
| BR-003 | Agent Role Required for Creation | The creating actor must be Agent, Supervisor, or System; Viewer cannot create (AC-1 presupposes an Agent) | Exercised |
| BR-004 | Duplicate Check Before Activation | Core gate rule: detection must run before Pending → Active; any flag must be resolved first | Exercised |
| BR-005 | System-Generated Customer ID | A customer_id is assigned to the new record at creation; it must persist unchanged through flag resolution, dismissal, or merge | Exercised |
| BR-006 | Initial Status is Pending | All new records begin in Pending; AC-2 is consistent with this rule | Exercised |
| BR-009 | One Record Per Verified Identity | National identifier is used as a matching field; two Active records with the same verified identity are prohibited | Exercised |
| BR-011 | Automatic Duplicate Flagging | The mechanism that executes AC-1 and AC-2; runs at point of creation against all Active and Pending records | Exercised |
| BR-014 | Duplicate Dismissal Requires Authorization | Governs AC-4 and the prohibition in AC-6; only Supervisor+ may dismiss; dismissal must include a written reason | Exercised |
| BR-015 | Duplicate Flag Blocks Activation | Governs AC-8; the Pending → Active transition is blocked while any open flag exists | Exercised |
| BR-016 | Allowed Status Transitions | The permitted transition matrix governs every lifecycle change in this flow: Pending → Active (after flag cleared), Pending → Active (no flag), and the merge-implied Pending → Merged path | Exercised |
| BR-022 | Status Change Propagated to Downstream | When the record transitions to Active after flag dismissal, a downstream event must be generated; also applies to any merge-triggered status change | Constrained by |
| BR-023 | At Least One Verified Contact Method | Dismissal clears the flag but does not activate the record; activation still requires a verified contact method — AC-4 overstates the effect of dismissal by saying the record "proceeds to Active" without noting this prerequisite | Constrained by |
| BR-032 | Merge Requires Supervisor Authorization | Governs AC-5 and the prohibition in AC-6; Agent cannot execute a merge | Exercised |
| BR-033 | Merge Designates One Survivor | The Supervisor must explicitly designate which record survives; AC-5 references this | Exercised |
| BR-034 | Merge is Irreversible | Once confirmed, the merge cannot be undone; the Notes section acknowledges this; constrains test scope | Constrained by |
| BR-035 | Non-Survivor Retained for Audit | After merge, the non-survivor record must be retained in Merged status with a reference to the survivor | Exercised |
| BR-036 | Only One Active Merge Per Record | A record already in an active merge cannot be included in a second concurrent merge; relevant to concurrency testing | Constrained by |
| BR-037 | Downstream Systems Notified on Merge | AC-5 explicitly requires downstream notification on merge completion; notification is asynchronous per LIM-024 | Exercised |
| BR-038 | Role-Based Access Enforcement | Every action (dismiss, merge, activate) must be evaluated against the actor's role before execution; AC-6 is the requirement-level expression of this rule | Exercised |
| BR-039 | Restricted Fields Require Elevated Role | National identifier is a restricted field (Sensitive — Restricted); Agents cannot view or edit it; this constrains test design for AC-7 national identifier matching tests | Constrained by |
| BR-043 | All Changes Produce Audit Entries | Flag creation, flag dismissal, merge initiation, merge confirmation, and status transitions must all produce audit events; not stated in any AC but required by this rule | Exercised |
| BR-051 | Validation Errors Returned with Field-Level Detail | Any creation rejection (missing fields, invalid email format) must return field-level error detail | Constrained by |
| BR-052 | Rejected Transitions Return Business Reason | AC-8 requires the rejection message to state the open Duplicate Flag reason; this rule governs the format of that message | Exercised |

---

## Impacted Entities and Fields

### Customer

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `customer_id` | Read | Immutable; system-generated at creation; must persist unchanged on survivor after merge | data-model.md Section 1; BR-005, BR-007 |
| `customer_type` | Create / Validate | `Individual` or `Organisation`; governs which name fields are required; immutable post-creation (LIM-002) | data-model.md Section 1; BR-001 |
| `first_name` | Create / Validate | 1–100 chars; not whitespace-only; Individual only; used as duplicate detection matching field | data-model.md Section 1; BR-048 |
| `last_name` | Create / Validate | 1–150 chars; not whitespace-only; Individual only; used as duplicate detection matching field | data-model.md Section 1; BR-048 |
| `national_identifier` | Validate | Optional; 5–20 alphanumeric chars; Restricted field (Supervisor+ only); used as matching field only when present on both records | data-model.md Section 1; BR-008, BR-039 |
| `status` | Validate / Update | Permitted values: `Pending`, `Active`, `Merged`; open Duplicate Flag blocks Pending → Active (BR-015); Pending → Merged via merge operation | data-model.md Section 1; BR-016 |
| `merged_into` | Update | Conditional — required when `status = Merged`; must reference the surviving customer_id; null otherwise | data-model.md Section 1; BR-010 |

### Email

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `email_address` | Create / Validate | RFC 5321 format; max 254 chars; normalised to lowercase on save; Primary email must be unique across Active and Pending records | data-model.md Section 3; BR-002, BR-024 |
| `email_type` | Validate | `Primary` or `Secondary`; only Primary email used as duplicate detection matching input; secondary emails not deduplicated (LIM-008) | data-model.md Section 3; BR-026 |
| `is_verified` | Validate | Must be `true` on at least one contact method before Pending → Active is permitted (BR-023) | data-model.md Section 3; BR-023 |
| `verified_at` | Validate | Required when `is_verified = true`; must not be null | data-model.md Section 3 |

### Phone

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `phone_number` | Create / Validate | E.164 format; max 15 digits after country code; normalised on save; Primary phone unique across Active and Pending records | data-model.md Section 4; BR-025, BR-026 |
| `phone_type` | Validate | `Primary`, `Mobile`, `Work`, or `Secondary`; only Primary phone used as duplicate detection matching input (LIM-008) | data-model.md Section 4 |

### Customer Status History

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `new_status` | Create | Must be a permitted transition from `previous_status` per BR-016; Pending → Active and Pending → Merged are the relevant transitions in this flow | data-model.md Section 6; BR-016 |
| `previous_status` | Create | Must reflect the actual prior status; null only on first transition | data-model.md Section 6 |
| `changed_by` | Create | Must reference the User who authorised the transition; not null | data-model.md Section 6 |
| `reason_code` | Create | Required for transitions to `Suspended` and `Closed`; not required for Pending → Active | data-model.md Section 6; BR-018 |

### Merge History

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `survivor_customer_id` | Create | Must reference the customer remaining Active after merge; must differ from `non_survivor_customer_id` | data-model.md Section 7; BR-033 |
| `non_survivor_customer_id` | Create | Must reference the customer transitioning to Merged; can appear as non-survivor in at most one record (BR-036); must differ from `survivor_customer_id` | data-model.md Section 7; BR-033, BR-036 |
| `initiated_by` | Create | Must reference a User with Supervisor role or above (BR-032) | data-model.md Section 7 |
| `confirmed_by` | Create | Must reference a User with Supervisor role or above; may be same as `initiated_by` | data-model.md Section 7 |
| `completed_at` | Create | UTC timestamp; must be ≥ `initiated_at` | data-model.md Section 7 |

### Audit Event

| Field | Operation | Constraint / Boundary | Source |
|---|---|---|---|
| `entity_type` | Create | `Customer` for record creation and status changes; `MergeHistory` for merge events | data-model.md Section 8; BR-043 |
| `action` | Create | `CREATE` for new record; `STATUS_CHANGE` for transitions; `MERGE` for merge operations | data-model.md Section 8; BR-043 |
| `performed_by` | Create | Must reference the acting User or system identity; not null | data-model.md Section 8 |
| `old_value` | Create | Present for `STATUS_CHANGE` and `UPDATE`; null for `CREATE` | data-model.md Section 8 |
| `new_value` | Create | Present for `CREATE`, `UPDATE`, and `STATUS_CHANGE` | data-model.md Section 8 |

---

## Relevant Known Limitations

| Limitation ID | Title | Impact on Requirement or Testing |
|---|---|---|
| LIM-008 | Secondary Contact Methods Are Not Deduplicated | Duplicate detection tests must use primary email and phone only; a secondary email match must not trigger a flag — confirm absence of flag as a negative test. |
| LIM-010 | Free-Text Fields Are Not Spell-Checked or Standardised | Name-based detection tests must account for configurable matching sensitivity; clear-match and clear-no-match scenarios are reliable test cases; near-match (e.g., "Smith" vs "SMITH") boundary behaviour is environment-dependent. |
| LIM-015 | Merge Cannot Be Partially Reversed | Tests must not expect or assert any post-merge reversal capability; generate a test confirming no reversal option is presented to any role. |
| LIM-016 | Merge Does Not Automatically Resolve Data Conflicts | Merge tests must verify the Supervisor is presented with both records' field values before confirming; the survivor's fields must remain unchanged if no selection is made by the Supervisor. |
| LIM-017 | Only Two Records Can Be Merged in a Single Operation | Do not generate tests expecting a three-or-more-record merge in one operation; this story's scope covers one merge at a time. |
| LIM-024 | Downstream Systems Are Notified Asynchronously | Integration tests for post-merge and post-activation downstream events must use asynchronous verification; do not assert an immediate downstream state change. |
| LIM-028 | Concurrent Merge Operations Are Serialised | A concurrency test where two Supervisors attempt to merge the same flagged record simultaneously must expect the second request to receive a conflict error, not a silent failure. |
| LIM-030 | Test Environments Do Not Receive Live Downstream Events | Integration tests must target downstream stubs; real downstream processing cannot be verified in non-production environments. |
| LIM-031 | Duplicate Detection Sensitivity Is Configurable and Environment-Specific | All duplicate detection tests must include a precondition step verifying matching thresholds are correctly set; near-match boundary tests are environment-dependent and must not be treated as universally reproducible. |

---

## Acceptance Criteria Assessment

| # | Criterion | Classification | Missing Information |
|---|---|---|---|
| AC-1 | Given I am a logged-in Agent, when I submit a new customer creation request, then the system must automatically run duplicate detection against all Active and Pending customer records before the record is saved. | Testable | None |
| AC-2 | Given duplicate detection identifies one or more potential matches, when the new customer record is created, then the system must raise a Duplicate Flag on the new record and retain its status as Pending. | Testable | None |
| AC-3 | Given a Duplicate Flag exists on a Pending record, when a Supervisor opens the flagged record, then the system must display the list of matching records alongside the flagged record to support comparison and review. | Testable | None — the trigger (Supervisor opens the record) and the expected display (list of matching records) are specific enough to test. The notification mechanism for alerting the Supervisor to the existence of the flag is not defined (see Q-1), but the display behaviour itself is testable. |
| AC-4 | Given a Duplicate Flag is open on a Pending record, when a Supervisor dismisses the flag and provides a written reason, then the flag is cleared and the record becomes eligible to transition to Active (subject to all other activation requirements being met). | Partially Testable | The definition of "written reason" is not specified: minimum character length, maximum character length, and whether a structured reason code is required alongside the free-text are all undefined. The positive path (non-empty reason → dismissal succeeds) is testable; boundary and negative tests for the reason field require clarification. |
| AC-5 | Given a Duplicate Flag is open on a Pending record, when a Supervisor initiates a merge and designates the survivor record, then the system must complete the merge, set the non-survivor to Merged status, link the non-survivor to the survivor, and notify all downstream systems. | Partially Testable | The intermediate steps of the merge workflow between initiation and confirmation are not described. Whether the Supervisor is presented with both records' field values for selective retention before confirming (required by LIM-016) is not specified in this story. The outcomes stated in the criterion are testable; the workflow steps are not. |
| AC-6 | Given a Duplicate Flag is open on a Pending record, when an Agent attempts to dismiss the flag or initiate a merge, then the system must reject the action and return a clear error message indicating that Supervisor authorisation is required. | Testable | None |
| AC-7 | The duplicate detection algorithm must evaluate the following fields when comparing a new record against existing records: first name, last name, primary email address, primary phone number, and national identifier (when provided on both records being compared). | Partially Testable | The matching logic is unspecified: whether ALL listed fields must match, ANY single field match is sufficient, or a weighted confidence score above a configurable threshold is required is not stated. Per LIM-031, sensitivity is environment-specific. Clear all-match and clear no-match scenarios are testable; threshold boundary behaviour is not deterministically testable without this information. |
| AC-8 | Given a Pending record has an open Duplicate Flag, when an Agent attempts to transition the record to Active, then the system must reject the transition and return a message stating that an open Duplicate Flag must be resolved first. | Testable | None |

---

## Ambiguities and Missing Information

1. **AC-3 — Supervisor notification mechanism:** AC-3 specifies that when a Supervisor opens a flagged record, the matching records are displayed. However, the requirement does not describe how the Supervisor is informed that a Duplicate Flag exists on a record they have not yet opened. Is there a dedicated duplicate review queue? An in-portal notification banner? No proactive notification (Supervisor must search)? This affects how test preconditions are set up and whether a notification test area is needed.

2. **AC-4 — Definition of "written reason" for dismissal:** BR-014 requires "a written reason" for flag dismissal but neither the rule nor this requirement defines the format, minimum length, maximum length, or whether a structured reason code must accompany the free-text field. What constitutes a valid vs. invalid dismissal reason?

3. **AC-5 — Merge workflow intermediate steps:** AC-5 describes the outcome of a merge but not the steps between initiation and confirmation. Given LIM-016 (merge does not auto-resolve data conflicts), the Supervisor must select which non-survivor fields to retain. Is this field selection presented as part of the merge initiation in this story, or is it a separate workflow step? What is shown to the Supervisor before they confirm?

4. **AC-7 — Matching algorithm and confidence threshold:** The requirement lists the fields to match on but not the matching logic. Is a flag raised when any single field matches, when a majority match, or when a configurable confidence score is exceeded? This is particularly important for the name fields, which are free-text and subject to case and spelling variation (LIM-010, LIM-031).

5. **AC-4 — Dismissal does not guarantee activation:** AC-4 states that after dismissal the record "becomes eligible to transition to Active." However, BR-023 requires at least one verified contact method before a Pending → Active transition can succeed. A record with no verified contact method would have its flag dismissed but still cannot be activated. This is not a conflict — the parenthetical "(subject to all other activation requirements being met)" covers it — but it creates an implicit test dependency that is not explicitly stated in the criterion.

6. **No acceptance criterion for audit events:** BR-043 requires every flag creation, dismissal, and merge to produce an Audit Event. No AC in this story explicitly requires audit logging for these actions. Audit testing is required by the knowledge base but is not stated in the requirement.

7. **No acceptance criterion for downstream notification after dismissal+activation:** BR-022 requires a downstream event when a record transitions from Pending to Active. No AC addresses this downstream notification path. It is required by the knowledge base.

8. **Pending → Merged status transition path:** BR-016's permitted transition matrix (Pending → Active, Pending → Closed; no explicit Pending → Merged entry) does not list a Pending → Merged path. When the Pending new record is the non-survivor in a merge, does it transition directly to Merged from Pending? This affects lifecycle test preconditions.

---

## Conflicts and Risks

1. **[INFERRED] AC-4 overstates the effect of dismissal vs. BR-023:** The criterion states dismissal "allows the record to proceed to Active" without explicitly noting that BR-023 (At Least One Verified Contact Method) is an independent gate. Dismissal removes the flag as a blocking condition but does not guarantee activation. If a test is designed expecting dismissal → immediate activation with no verified contact method, it will fail. This is not a contradiction — the parenthetical in AC-4 covers it — but the phrasing is misleading and may lead the Test Generation Agent to generate an incorrect positive test.

2. **[INFERRED] BR-016 transition matrix does not explicitly include Pending → Merged:** The permitted transition matrix in BR-016 lists Pending → Active and Pending → Closed. A Pending → Merged path (which occurs when the new record is the non-survivor) is implied by the merge mechanics but is not explicitly validated by the matrix. If the transition engine validates strictly against BR-016, this path may be rejected as an invalid transition. This is an ambiguity, not a confirmed conflict — Q-5 addresses it.

No confirmed direct contradictions between requirement statements and business rules identified.

---

## Recommended Test Areas

| Test Area | Applicable | Reason |
|---|---|---|
| Positive | Yes | Happy path: Agent creates customer with no matching records; no flag raised; Agent proceeds to activate without impediment. Second path: flag raised, Supervisor dismisses with reason, record then activated. Third path: flag raised, Supervisor merges, survivor remains Active. |
| Negative | Yes | Agent attempts flag dismissal (AC-6); Agent attempts merge initiation (AC-6); Agent attempts Pending → Active while flag open (AC-8); creation with missing mandatory fields; invalid email format; empty dismissal reason. |
| Boundary | Yes | Email at 254 chars (accepted) and 255 chars (rejected); first_name at 100 chars (accepted) and 101 chars (rejected); national_identifier at 5 chars (min accepted) and 20 chars (max accepted) and 4/21 chars (rejected); phone E.164 max 15 digits. |
| Permission | Yes | Agent vs Supervisor capabilities differ across dismissal and merge; Viewer has no create, dismiss, or merge permissions; all five roles should be verified against their expected outcomes on key actions. |
| Lifecycle | Yes | Pending → Active blocked by open flag (AC-8); Pending → Active permitted after flag dismissed and verified contact exists; Pending → Merged as non-survivor via merge; survivor record status unchanged post-merge; Merged status is terminal for non-survivor. |
| Integration | Yes | Downstream notification on Pending → Active transition after flag dismissal (BR-022); downstream merge event on merge completion (BR-037); both notifications are asynchronous (LIM-024); test environment stub must be used (LIM-030). |
| Data Validation | Yes | Email RFC 5321 format (BR-024); phone E.164 format and normalisation (BR-025); first/last name whitespace-only rejection (BR-048); national identifier length and format constraints (BR-008); primary email uniqueness across Active and Pending (BR-002). |
| Concurrency | Yes | Two Supervisors simultaneously attempting to merge the same flagged record; second request must receive a conflict error per LIM-028 and BR-036. |
| Audit | Yes | Flag creation, flag dismissal, and merge must each produce Audit Events with correct `action`, `entity_type`, `entity_id`, `performed_by`, and `performed_at` fields (BR-043). Audit events must be immutable (BR-044). |

---

## Risk Classification

**Level:** High

This requirement activates one irreversible operation (merge, governed by BR-034) and two lifecycle transitions across multiple entities. It involves role-based access controls spanning five distinct prohibited and permitted action combinations (BR-038, BR-014, BR-032), downstream integration events to four systems (BR-022, BR-037), and a restricted field (national identifier, BR-039) embedded in the detection algorithm. The unresolved ambiguity on the matching algorithm threshold (Q-2) means that boundary tests for duplicate detection cannot be written with precision and may produce non-deterministic results across environments (LIM-031). Additionally, AC-4's implicit dependency on BR-023 creates a risk of an incorrectly written positive test expecting immediate activation after dismissal. The combination of an irreversible merge path, multiple integration events, restricted field access, and partially testable acceptance criteria places this firmly at High. It does not reach Critical because no compliance-primary field (consent) is the central subject, and no acceptance criterion is entirely Not Testable.

---

## Assumptions

| # | Assumption | Type | Source |
|---|---|---|---|
| A-1 | The "duplicate review workflow" referenced in AC-5 is the Duplicate Management functional area described in application-context.md Section 7. | Knowledge-Based | application-context.md Section 7 |
| A-2 | Duplicate detection runs at the point of record creation, before the record is saved, as stated in BR-011. AC-1 is consistent with this rule. | Knowledge-Based | business-rules.md BR-011 |
| A-3 | AC-4's statement that dismissal "allows the record to proceed to Active" means it removes the Duplicate Flag as a blocking condition. The record must still satisfy BR-023 (verified contact method) and all other activation requirements before the Pending → Active transition can execute. Dismissal alone does not activate the record. | Knowledge-Based | business-rules.md BR-015, BR-023 |
| A-4 | The "written reason" required by AC-4 corresponds to the written reason required by BR-014. No additional structured reason code is implied by either source; however, the format of the written reason (minimum/maximum length) is undefined in both. | Knowledge-Based | business-rules.md BR-014 |
| A-5 | AC-7's condition "when provided on both records" for national identifier matching means the flag is raised on national identifier only when BOTH the new and the matched existing record have the field populated. A match is not triggered if only one record carries a national identifier. | Inferred | business-rules.md BR-009; data-model.md Section 1 |
| A-6 | Secondary email addresses and secondary phone numbers are explicitly excluded from matching per the requirement Notes and LIM-008. This adds no constraint beyond what the knowledge base already states. | Knowledge-Based | known-limitations.md LIM-008 |
| A-7 | A Pending record may transition directly to Merged status as a non-survivor without passing through Active first. The BR-016 transition matrix does not explicitly list this path, but the merge mechanism operates independently of the standard status transition gate. | Unverified | None — Q-5 raises this for product owner confirmation |
| A-8 | Duplicate detection is triggered by the system at the moment of creation (AC-1), not by a manual Agent action. The Agent submits the record; the system runs detection automatically. | Knowledge-Based | business-rules.md BR-011 |

---

## Questions for Product Owner

1. **(Q-1 — Non-blocking)** AC-3 specifies that when a Supervisor opens a flagged record, the matching records are displayed. How is the Supervisor informed that a flagged record requiring their review exists? Specifically: (a) Is there a dedicated duplicate review queue populated automatically when a flag is raised? (b) Is there an in-portal alert or notification badge visible on the Supervisor's next login? (c) Or must the Supervisor discover flagged records through search? This affects whether a proactive notification test area is needed.

2. **(Q-2 — Non-blocking)** AC-4 requires the Supervisor to provide "a written reason" when dismissing a flag. What defines a valid written reason? Specifically: (a) Is there a minimum character length (e.g., 10 characters)? (b) Is there a maximum character length? (c) Is a structured reason code required in addition to the free-text reason, or is free-text alone sufficient? This affects boundary test design for dismissal validation.

3. **(Q-3 — Non-blocking)** AC-5 designates the Supervisor as selecting the survivor record. Can the new Pending record be designated as the Survivor (making the existing Active record the Non-Survivor), or must the existing Active record always survive? BR-033 imposes no restriction, but there may be an operational convention.

4. **(Q-4 — Non-blocking)** The Notes section explicitly states that update-triggered detection (BR-012) is out of scope for this story. Can you confirm whether a separate story covers the case where an Agent updates an existing Active customer's primary contact to a value already held by another Active record? This is needed to confirm the scope boundary for integration tests.

5. **(Q-5 — Non-blocking)** When the new Pending record is the Non-Survivor in a merge, what is the status transition path? Does it transition directly Pending → Merged, or does a different mechanism apply? The BR-016 transition matrix does not explicitly list a Pending → Merged path; clarification is needed to write correct lifecycle test preconditions.

---

## Handoff Package

```yaml
handoff:
  requirement_id: "US-042"
  risk_level: "High"
  ready_for_test_generation: true
  blocker_reason: null

  summary:
    business_objective: >
      Prevent duplicate Active customer records by gating activation on automated
      duplicate detection and Supervisor-authorised resolution, preserving the
      organisation's customer master data as a single accurate source of truth.
    feature_areas:
      - "Duplicate detection"
      - "Customer record management"
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
    - id: "BR-002"
      title: "Unique Email on Creation"
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
      relationship: "Constrained by"
    - id: "BR-023"
      title: "At Least One Verified Contact Method"
      relationship: "Constrained by"
    - id: "BR-032"
      title: "Merge Requires Supervisor Authorization"
      relationship: "Exercised"
    - id: "BR-033"
      title: "Merge Designates One Survivor"
      relationship: "Exercised"
    - id: "BR-034"
      title: "Merge is Irreversible"
      relationship: "Constrained by"
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
      relationship: "Constrained by"
    - id: "BR-052"
      title: "Rejected Transitions Return Business Reason"
      relationship: "Exercised"

  impacted_entities:
    - entity: "Customer"
      fields:
        - name: "customer_id"
          operation: "Read"
          constraint: "Immutable; system-generated; preserved on survivor post-merge (BR-005, BR-007)"
        - name: "customer_type"
          operation: "Create"
          constraint: "Individual or Organisation; governs required name fields; immutable after creation (LIM-002)"
        - name: "first_name"
          operation: "Create / Validate"
          constraint: "1–100 chars; not whitespace-only (BR-048); Individual only; used as duplicate detection matching field"
        - name: "last_name"
          operation: "Create / Validate"
          constraint: "1–150 chars; not whitespace-only (BR-048); Individual only; used as duplicate detection matching field"
        - name: "national_identifier"
          operation: "Validate"
          constraint: "Optional; 5–20 alphanumeric chars; Restricted field — Supervisor+ only (BR-039); matching field only when present on both records"
        - name: "status"
          operation: "Validate / Update"
          constraint: "Open Duplicate Flag blocks Pending→Active (BR-015); Pending→Merged implied by merge operation (Q-5 unresolved)"
        - name: "merged_into"
          operation: "Update"
          constraint: "Required when status=Merged; must reference surviving customer_id; null otherwise (BR-010)"
    - entity: "Email"
      fields:
        - name: "email_address"
          operation: "Create / Validate"
          constraint: "RFC 5321 format; max 254 chars; lowercase on save; Primary email unique across Active and Pending (BR-002)"
        - name: "email_type"
          operation: "Validate"
          constraint: "Only Primary used for duplicate matching; Secondary emails excluded from deduplication (LIM-008)"
        - name: "is_verified"
          operation: "Validate"
          constraint: "At least one verified contact method required before Pending→Active (BR-023)"
        - name: "verified_at"
          operation: "Validate"
          constraint: "Required when is_verified=true; must not be null"
    - entity: "Phone"
      fields:
        - name: "phone_number"
          operation: "Create / Validate"
          constraint: "E.164 format; max 15 digits; normalised on save; Primary phone unique across Active and Pending (BR-026)"
        - name: "phone_type"
          operation: "Validate"
          constraint: "Only Primary used for duplicate matching; Secondary phones excluded (LIM-008)"
    - entity: "Customer Status History"
      fields:
        - name: "new_status"
          operation: "Create"
          constraint: "Must be a permitted transition per BR-016; Pending→Active and Pending→Merged relevant to this flow"
        - name: "changed_by"
          operation: "Create"
          constraint: "Must reference the authorising User; not null"
    - entity: "Merge History"
      fields:
        - name: "survivor_customer_id"
          operation: "Create"
          constraint: "Must differ from non_survivor_customer_id; must reference Active post-merge record (BR-033)"
        - name: "non_survivor_customer_id"
          operation: "Create"
          constraint: "Must differ from survivor_customer_id; can appear as non-survivor in at most one record (BR-036)"
        - name: "initiated_by"
          operation: "Create"
          constraint: "Must reference User with Supervisor role or above (BR-032)"
        - name: "confirmed_by"
          operation: "Create"
          constraint: "Must reference User with Supervisor role or above; may equal initiated_by"
    - entity: "Audit Event"
      fields:
        - name: "action"
          operation: "Create"
          constraint: "CREATE for new record; STATUS_CHANGE for transitions; MERGE for merge operation (BR-043)"
        - name: "performed_by"
          operation: "Create"
          constraint: "Must reference the acting User or system identity"
        - name: "entity_type"
          operation: "Create"
          constraint: "Customer for record/status events; MergeHistory for merge events"

  relevant_limitations:
    - id: "LIM-008"
      title: "Secondary Contact Methods Are Not Deduplicated"
      testing_impact: "Duplicate detection tests must use primary email and phone only; secondary contact method matches must not trigger a flag."
    - id: "LIM-010"
      title: "Free-Text Fields Are Not Spell-Checked or Standardised"
      testing_impact: "Name-matching tests must use clear-match and clear-no-match data; near-match boundary tests are environment-dependent per LIM-031."
    - id: "LIM-015"
      title: "Merge Cannot Be Partially Reversed"
      testing_impact: "Do not generate tests expecting a merge reversal function; generate a test confirming no reversal option is exposed."
    - id: "LIM-016"
      title: "Merge Does Not Automatically Resolve Data Conflicts"
      testing_impact: "Merge tests must verify the Supervisor is presented with field values from both records before confirmation; survivor fields must remain unchanged if no selection is made."
    - id: "LIM-017"
      title: "Only Two Records Can Be Merged in a Single Operation"
      testing_impact: "Do not generate multi-record merge tests; one Survivor and one Non-Survivor per operation only."
    - id: "LIM-024"
      title: "Downstream Systems Are Notified Asynchronously"
      testing_impact: "Integration tests for post-merge and post-activation notifications must use async verification; no immediate downstream state assertion."
    - id: "LIM-028"
      title: "Concurrent Merge Operations Are Serialised"
      testing_impact: "Concurrency test must expect a conflict error on the second simultaneous merge request for the same record."
    - id: "LIM-030"
      title: "Test Environments Do Not Receive Live Downstream Events"
      testing_impact: "All integration tests must target downstream stubs; real downstream state cannot be verified in non-production."
    - id: "LIM-031"
      title: "Duplicate Detection Sensitivity Is Configurable and Environment-Specific"
      testing_impact: "All duplicate detection tests must include a precondition verifying threshold configuration; near-match boundary behaviour is not universally deterministic."

  test_areas:
    - area: "Positive"
      applicable: true
      reason: "Happy path: create with no match, no flag; create with match, flag raised, Supervisor dismisses, record activated; create with match, Supervisor merges."
    - area: "Negative"
      applicable: true
      reason: "Agent attempts dismissal; Agent attempts merge; Agent attempts activation with open flag; creation with missing fields; invalid email format; empty dismissal reason."
    - area: "Boundary"
      applicable: true
      reason: "Email 254/255 chars; first_name 100/101 chars; national_identifier 5/4 and 20/21 chars; phone E.164 digit limits."
    - area: "Permission"
      applicable: true
      reason: "Viewer, Agent, Supervisor, Administrator, and System each have different outcomes on dismiss and merge actions."
    - area: "Lifecycle"
      applicable: true
      reason: "Pending→Active blocked by open flag; Pending→Active after dismissal + verified contact; Pending→Merged as non-survivor; Merged status terminal for non-survivor."
    - area: "Integration"
      applicable: true
      reason: "Downstream notification on activation (BR-022) and on merge completion (BR-037); both asynchronous (LIM-024)."
    - area: "Data Validation"
      applicable: true
      reason: "Email format (BR-024); phone E.164 format (BR-025); name whitespace (BR-048); national identifier length and format (BR-008); primary uniqueness (BR-002, BR-026)."
    - area: "Concurrency"
      applicable: true
      reason: "Two simultaneous merge attempts on the same flagged record must yield a conflict error on the second (LIM-028, BR-036)."
    - area: "Audit"
      applicable: true
      reason: "Flag creation, dismissal, and merge must each produce an Audit Event with correct fields (BR-043); audit records must be immutable (BR-044)."

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
      classification: "Testable"
      missing_information: null
    - id: "AC-4"
      text: "Given a Duplicate Flag is open on a Pending record, when a Supervisor dismisses the flag and provides a written reason, then the flag is cleared and the record becomes eligible to transition to Active, subject to all other activation requirements being met."
      classification: "Partially Testable"
      missing_information: "Minimum and maximum length of the written reason, and whether a structured reason code is also required, are not defined. Positive path (non-empty reason → success) is testable; boundary tests for the reason field are not."
    - id: "AC-5"
      text: "Given a Duplicate Flag is open on a Pending record, when a Supervisor initiates a merge and designates the survivor record, then the system must complete the merge, set the non-survivor to Merged status, link the non-survivor to the survivor, and notify all downstream systems."
      classification: "Partially Testable"
      missing_information: "Intermediate merge workflow steps (field value review per LIM-016) are not described. Outcomes stated in the criterion are testable; workflow step sequence is not."
    - id: "AC-6"
      text: "Given a Duplicate Flag is open on a Pending record, when an Agent attempts to dismiss the flag or initiate a merge, then the system must reject the action and return a clear error message indicating that Supervisor authorisation is required."
      classification: "Testable"
      missing_information: null
    - id: "AC-7"
      text: "The duplicate detection algorithm must evaluate the following fields: first name, last name, primary email address, primary phone number, and national identifier (when provided on both records)."
      classification: "Partially Testable"
      missing_information: "Matching logic not defined: ALL-field match, ANY-field match, or weighted confidence score. Per LIM-031, threshold is configurable. Clear all-match and no-match scenarios are testable; threshold boundary is not."
    - id: "AC-8"
      text: "Given a Pending record has an open Duplicate Flag, when an Agent attempts to transition the record to Active, then the system must reject the transition and return a message stating that an open Duplicate Flag must be resolved first."
      classification: "Testable"
      missing_information: null

  boundary_conditions:
    - field: "email_address"
      entity: "Email"
      condition: "254 characters: accepted. 255 characters: rejected. Source: data-model.md Section 3."
    - field: "email_address"
      entity: "Email"
      condition: "Missing @ symbol: rejected — invalid RFC 5321 format (BR-024). Source: data-model.md — Test-Data Boundaries."
    - field: "email_address"
      entity: "Email"
      condition: "Uppercase characters: accepted and normalised to lowercase on save. Source: data-model.md Section 3."
    - field: "first_name"
      entity: "Customer"
      condition: "100 characters: accepted (maximum). 101 characters: rejected. Whitespace-only: rejected (BR-048). Source: data-model.md Section 1."
    - field: "last_name"
      entity: "Customer"
      condition: "150 characters: accepted (maximum). 151 characters: rejected. Whitespace-only: rejected (BR-048). Source: data-model.md Section 1."
    - field: "national_identifier"
      entity: "Customer"
      condition: "5 characters: accepted (minimum). 4 characters: rejected. 20 characters: accepted (maximum). 21 characters: rejected. Source: data-model.md — Test-Data Boundaries."
    - field: "phone_number"
      entity: "Phone"
      condition: "Without + country prefix: rejected or normalised depending on input mode. Fewer than 7 digits after country code: rejected. More than 15 digits total: rejected (E.164 max). Source: data-model.md — Test-Data Boundaries."
    - field: "status"
      entity: "Customer"
      condition: "Any transition not in the BR-016 permitted matrix: rejected with business reason (BR-052). Source: data-model.md — Test-Data Boundaries."

  invalid_combinations:
    - description: "`status = Active` with no verified email or phone"
      relevant_because: "After flag dismissal, the record becomes eligible for activation but cannot transition to Active without a verified contact method (BR-023). A test expecting dismissal to directly result in activation would fail."
    - description: "`status = Merged` with `merged_into = null`"
      relevant_because: "The non-survivor record after merge must have `merged_into` populated with the survivor's customer_id (BR-010). A Merged record without this reference is invalid."
    - description: "`survivor_customer_id` equals `non_survivor_customer_id` in a Merge History record"
      relevant_because: "A record cannot be merged with itself; this combination must be rejected. Source: data-model.md — Invalid Data Combinations."
    - description: "`non_survivor_customer_id` already appearing in an existing Merge History record as non-survivor"
      relevant_because: "A record can only be the non-survivor of one merge operation (BR-036). A second merge attempt using an already-merged record as non-survivor must be rejected."
    - description: "`User.role_id` = Viewer or Agent attempting Duplicate Flag dismissal or merge initiation"
      relevant_because: "Only Supervisor and above may dismiss (BR-014) or merge (BR-032). Agent and Viewer attempts must be rejected with an explicit authorisation error (AC-6)."
    - description: "`is_verified = true` with `verified_at = null` on an Email or Phone record"
      relevant_because: "Verification timestamp is required when is_verified is true. A contact method cannot be marked verified without a timestamp. Source: data-model.md — Invalid Data Combinations."

  open_questions:
    - id: "Q-1"
      question: "How is a Supervisor informed that a Duplicate Flag has been raised on a record they have not yet opened? Is there a dedicated duplicate review queue, an in-portal notification, or no proactive notification? This affects whether a proactive notification test area is needed."
      blocking: false
    - id: "Q-2"
      question: "What defines a valid 'written reason' for flag dismissal per AC-4? Specifically: minimum character length, maximum character length, and whether a structured reason code is required in addition to free-text."
      blocking: false
    - id: "Q-3"
      question: "Can the new Pending record be designated as the Survivor in a merge (making the existing Active record the Non-Survivor), or must the existing Active record always be the Survivor? BR-033 imposes no restriction; confirm if there is an operational convention."
      blocking: false
    - id: "Q-4"
      question: "Can you confirm that update-triggered duplicate detection (BR-012) is handled by a separate story, and that this story covers creation-triggered detection only? This is needed to define the scope boundary for integration tests."
      blocking: false
    - id: "Q-5"
      question: "When a Pending record is the Non-Survivor in a merge, what is the status transition path? Does it go directly Pending → Merged, or does a different mechanism apply? The BR-016 transition matrix does not explicitly list a Pending → Merged path."
      blocking: false

  conflicts: []

  assumptions:
    - text: "The duplicate review workflow (AC-5) is the Duplicate Management functional area described in application-context.md Section 7."
      type: "Knowledge-Based"
      source: "application-context.md Section 7"
    - text: "Duplicate detection runs at the point of record creation, before the record is saved, consistent with BR-011."
      type: "Knowledge-Based"
      source: "business-rules.md BR-011"
    - text: "Dismissal removes the Duplicate Flag as a blocking condition but does not guarantee activation. BR-023 (verified contact method) is an independent gate that must also be satisfied."
      type: "Knowledge-Based"
      source: "business-rules.md BR-015, BR-023"
    - text: "The written reason for dismissal in AC-4 corresponds to the written reason required by BR-014. No additional structured reason code is implied by either the requirement or the rule, though the format is undefined."
      type: "Knowledge-Based"
      source: "business-rules.md BR-014"
    - text: "National identifier matching fires only when BOTH the new record and the candidate match have the field populated. A match is not triggered when only one record carries a national identifier."
      type: "Inferred"
      source: "business-rules.md BR-009; data-model.md Section 1"
    - text: "Secondary email and phone exclusion from detection (Notes section) adds no constraint beyond LIM-008."
      type: "Knowledge-Based"
      source: "known-limitations.md LIM-008"
    - text: "A Pending record may transition directly to Merged status as a non-survivor without passing through Active first. This path is implied by the merge mechanics but is not explicitly listed in the BR-016 transition matrix."
      type: "Unverified"
      source: null
```
