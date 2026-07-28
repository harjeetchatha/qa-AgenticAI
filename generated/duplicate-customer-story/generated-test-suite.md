# Test Suite — US-042: Duplicate Customer Detection

**Requirement:** US-042 — Duplicate Customer Story
**POC Mode:** true | **Max Tests:** 10 | **Generated:** 10

---

## TC-001 — Agent Creates Customer with No Duplicate Match — No Flag Raised

- **Requirement:** US-042 — Duplicate detection runs on creation; no flag raised when no match found.
- **Objective:** Verify that when an Agent creates a customer record with unique identifying fields, the system completes creation, assigns Pending status, and raises no Duplicate Flag.
- **Priority:** P2-High
- **Test Type:** Positive
- **Confidence:** [CERTAIN]
- **Related Business Rules:** BR-001 — Mandatory Fields on Creation, BR-003 — Agent Role Required for Creation, BR-006 — Initial Status is Pending, BR-011 — Automatic Duplicate Flagging
- **Related Limitations:** LIM-031 — Duplicate Detection Sensitivity Is Configurable and Environment-Specific
- **Preconditions:**
  1. The acting user has Agent role and is authenticated.
  2. No existing Active or Pending customer record shares the test email, phone, or national identifier values below.
  3. Duplicate detection thresholds are confirmed in the test environment (LIM-031 precondition).
- **Test Data:**
  - `customer_type`: `Individual` — valid enum value per data-model.md Section 1
  - `first_name`: `Unique` — distinct value with no near-match in the system
  - `last_name`: `Testperson` — distinct value with no near-match in the system
  - `email_address` (Primary): `unique.testperson@example.com` — RFC 5321 format; under 254 chars; not held by any Active/Pending record
  - `phone_number` (Primary): `+441234567890` — E.164 format; not held by any Active/Pending record
  - `region`: a configured region value matching the Agent's assigned region

### Steps
1. Log in as a user with Agent role.
2. Submit a new customer creation request with the test data above.
3. Observe the system response.
4. Retrieve the newly created customer record.

### Expected Results
1. The system accepts the creation request and returns a success response.
2. A `customer_id` (UUID) is assigned by the system (BR-005).
3. The customer record has `status = Pending` (BR-006).
4. No Duplicate Flag is present on the record (BR-011 — detection found no matches).
5. An Audit Event with `action = CREATE` and `entity_type = Customer` is produced (BR-043).

### Assumptions
- [CERTAIN]: When no matches are found, the system must not block creation (requirement Notes section; BR-011).
- [INFERRED]: Q-8 is non-blocking; no additional review step exists for unmatched records (Q-8 has `blocking_for_specific_tests: false`).

### Open Questions
- None.

### Automation Candidate
Yes — deterministic inputs and outputs; no human judgement required; suitable for regression suite.

---

## TC-002 — Agent Creates Customer with Exact Email Match — Duplicate Flag Raised, Status Remains Pending

- **Requirement:** US-042 — Duplicate detection flags new record when match found; status remains Pending.
- **Objective:** Verify that when a new customer is created with a primary email already held by an Active customer, the system raises a Duplicate Flag and retains the new record's status as Pending.
- **Priority:** P1-Critical
- **Test Type:** Positive
- **Confidence:** [CERTAIN]
- **Related Business Rules:** BR-004 — Duplicate Check Before Activation, BR-006 — Initial Status is Pending, BR-011 — Automatic Duplicate Flagging, BR-015 — Duplicate Flag Blocks Activation
- **Related Limitations:** LIM-031 — Duplicate Detection Sensitivity Is Configurable and Environment-Specific
- **Preconditions:**
  1. An existing Active customer record (CUST-EXISTING) exists with `first_name = John`, `last_name = Matching`, primary email `john.matching@example.com`, primary phone `+441111111111`.
  2. The acting user has Agent role and is authenticated.
  3. Duplicate detection thresholds are confirmed in the test environment (LIM-031 precondition).
- **Test Data:**
  - `customer_type`: `Individual`
  - `first_name`: `John`
  - `last_name`: `Matching`
  - `email_address` (Primary): `john.matching@example.com` — identical to CUST-EXISTING primary email
  - `phone_number` (Primary): `+442222222222` — different phone to isolate email as the matching signal
  - `region`: configured region value matching the Agent's region

### Steps
1. Log in as a user with Agent role.
2. Submit a new customer creation request with the test data above.
3. Observe the system response.
4. Retrieve the newly created customer record.

### Expected Results
1. The system accepts the creation request and creates the new record.
2. The new record has `status = Pending` (BR-006; AC-2).
3. A Duplicate Flag is raised on the new record (BR-011; AC-2).
4. The new record is not set to Active (BR-015).
5. An Audit Event with `action = CREATE` is produced for the new customer (BR-043).

### Assumptions
- [INFERRED]: The Duplicate Flag is represented on the Customer record or a linked entity per BR-011 and glossary definition; physical representation is subject to Q-1.

### Open Questions
- Q-1: The data model does not define the Duplicate Flag field or entity. Flag-presence assertions are verified behaviourally (record blocked from Active); data-state assertions on the flag field itself are deferred pending Q-1 resolution.

### Automation Candidate
Yes — deterministic; suitable for regression once Q-1 is resolved for data-state assertions.

---

## TC-003 — Agent Attempts to Activate Pending Record with Open Duplicate Flag — Rejected

- **Requirement:** US-042 — AC-8: Agent cannot transition Pending record with open Duplicate Flag to Active.
- **Objective:** Verify that when an Agent attempts to transition a Pending record with an open Duplicate Flag to Active, the system rejects the transition and returns a message citing the open flag.
- **Priority:** P1-Critical
- **Test Type:** Negative
- **Confidence:** [CERTAIN]
- **Related Business Rules:** BR-015 — Duplicate Flag Blocks Activation, BR-038 — Role-Based Access Enforcement, BR-052 — Rejected Transitions Return Business Reason
- **Related Limitations:** None.
- **Preconditions:**
  1. A Pending customer record (CUST-FLAGGED) exists with an open Duplicate Flag (created via the flow verified in TC-002 or equivalent setup).
  2. The acting user has Agent role and is authenticated.
- **Test Data:**
  - `customer_id`: CUST-FLAGGED (Pending, open Duplicate Flag)
  - `target_status`: `Active`

### Steps
1. Log in as a user with Agent role.
2. Attempt to transition CUST-FLAGGED from Pending to Active.
3. Observe the system response.

### Expected Results
1. The system rejects the transition (BR-015; AC-8).
2. The response includes a message stating that an open Duplicate Flag must be resolved before activation (BR-052; AC-8).
3. CUST-FLAGGED remains in `status = Pending`.
4. No Customer Status History record is created for this rejected transition.
5. No Audit Event is created for a status change (the change did not occur).

### Assumptions
- [CERTAIN]: BR-015 blocks Pending → Active while a Duplicate Flag is open; BR-052 requires the rejection message to state the business reason.

### Open Questions
- None.

### Automation Candidate
Yes — deterministic rejection; suitable for regression.

---

## TC-004 — Agent Attempts to Dismiss Duplicate Flag — Rejected with Supervisor Authorisation Error

- **Requirement:** US-042 — AC-6: Agent cannot dismiss Duplicate Flag; system returns error requiring Supervisor authorisation.
- **Objective:** Verify that when an Agent attempts to dismiss an open Duplicate Flag, the system rejects the action and returns an error message stating Supervisor authorisation is required.
- **Priority:** P1-Critical
- **Test Type:** Permission
- **Confidence:** [CERTAIN]
- **Related Business Rules:** BR-014 — Duplicate Dismissal Requires Authorization, BR-038 — Role-Based Access Enforcement, BR-051 — Validation Errors Returned with Field-Level Detail
- **Related Limitations:** None.
- **Preconditions:**
  1. A Pending customer record (CUST-FLAGGED) exists with an open Duplicate Flag.
  2. The acting user has Agent role and is authenticated.
- **Test Data:**
  - `customer_id`: CUST-FLAGGED (Pending, open Duplicate Flag)
  - `action`: dismiss Duplicate Flag
  - `dismissal_reason`: `Not a duplicate — different address` — a plausible reason (testing that even a valid reason is insufficient for an Agent)

### Steps
1. Log in as a user with Agent role.
2. Attempt to dismiss the Duplicate Flag on CUST-FLAGGED, providing a written reason.
3. Observe the system response.

### Expected Results
1. The system rejects the dismissal action (BR-014; AC-6).
2. The response includes an error message indicating that Supervisor authorisation is required (BR-051; AC-6).
3. The Duplicate Flag remains open on CUST-FLAGGED.
4. CUST-FLAGGED remains in `status = Pending`.

### Assumptions
- [CERTAIN]: BR-014 explicitly requires Supervisor role or above for flag dismissal; BR-038 enforces role-based rejection, not silent failure.

### Open Questions
- None.

### Automation Candidate
Yes — deterministic permission rejection; suitable for regression.

---

## TC-005 — Agent Attempts to Initiate Merge — Rejected with Supervisor Authorisation Error

- **Requirement:** US-042 — AC-6: Agent cannot initiate a merge; system returns error requiring Supervisor authorisation.
- **Objective:** Verify that when an Agent attempts to initiate a merge on a flagged Pending record, the system rejects the action and returns an error message stating Supervisor authorisation is required.
- **Priority:** P1-Critical
- **Test Type:** Permission
- **Confidence:** [CERTAIN]
- **Related Business Rules:** BR-032 — Merge Requires Supervisor Authorization, BR-038 — Role-Based Access Enforcement, BR-051 — Validation Errors Returned with Field-Level Detail
- **Related Limitations:** None.
- **Preconditions:**
  1. A Pending customer record (CUST-FLAGGED) exists with an open Duplicate Flag alongside an existing Active match record (CUST-MATCH).
  2. The acting user has Agent role and is authenticated.
- **Test Data:**
  - `customer_id`: CUST-FLAGGED (Pending, open Duplicate Flag)
  - `action`: initiate merge
  - `survivor_designation`: CUST-MATCH

### Steps
1. Log in as a user with Agent role.
2. Attempt to initiate a merge on CUST-FLAGGED, designating CUST-MATCH as the survivor.
3. Observe the system response.

### Expected Results
1. The system rejects the merge initiation (BR-032; AC-6).
2. The response includes an error message indicating that Supervisor authorisation is required (BR-051; AC-6).
3. No Merge History record is created.
4. Both CUST-FLAGGED and CUST-MATCH remain in their pre-attempt statuses.

### Assumptions
- [CERTAIN]: BR-032 explicitly requires Supervisor role or above for merge initiation; BR-038 enforces role-based rejection.

### Open Questions
- None.

### Automation Candidate
Yes — deterministic permission rejection; suitable for regression.

---

## TC-006 — Supervisor Dismisses Duplicate Flag with Written Reason — Record Eligible for Activation

- **Requirement:** US-042 — AC-4: Supervisor dismisses Duplicate Flag with written reason; flag cleared; record becomes eligible for Active.
- **Objective:** Verify that a Supervisor can successfully dismiss a Duplicate Flag by providing a written reason, the flag is cleared, and the record can subsequently transition to Active when all other activation requirements are met.
- **Priority:** P1-Critical
- **Test Type:** Lifecycle
- **Confidence:** [CERTAIN]
- **Related Business Rules:** BR-014 — Duplicate Dismissal Requires Authorization, BR-015 — Duplicate Flag Blocks Activation, BR-023 — At Least One Verified Contact Method, BR-043 — All Changes Produce Audit Entries
- **Related Limitations:** None.
- **Preconditions:**
  1. A Pending customer record (CUST-FLAGGED) exists with an open Duplicate Flag.
  2. CUST-FLAGGED has at least one verified primary contact method (`is_verified = true`, `verified_at` populated).
  3. The acting user has Supervisor role and is authenticated.
- **Test Data:**
  - `customer_id`: CUST-FLAGGED (Pending, open Duplicate Flag)
  - `dismissal_reason`: `Records reviewed — different date of birth and address; confirmed not a duplicate` — non-empty written reason (BR-014)

### Steps
1. Log in as a user with Supervisor role.
2. Open the flagged record CUST-FLAGGED.
3. Dismiss the Duplicate Flag, providing the written reason above.
4. Observe the dismissal response.
5. Attempt to transition CUST-FLAGGED from Pending to Active.
6. Observe the activation response.

### Expected Results
1. The dismissal is accepted by the system (BR-014; AC-4).
2. The Duplicate Flag is cleared on CUST-FLAGGED (AC-4).
3. An Audit Event is produced capturing the dismissal action (BR-043).
4. The Pending → Active transition in step 5 is accepted (BR-015 no longer blocks; BR-016 permits Pending → Active for Agent+ role).
5. CUST-FLAGGED has `status = Active` after step 5.
6. A Customer Status History record is created for the Pending → Active transition.

### Assumptions
- [INFERRED]: Q-7 ("all other activation requirements") resolved per handoff assumption A-7 — verified contact method (BR-023) is the key additional prerequisite, captured in preconditions.
- [UNCERTAIN]: Storage location for the written dismissal reason is unresolved (Q-6); step 3 submits the reason but data-state assertion for where it is persisted is deferred.

### Open Questions
- Q-6: Where is the written dismissal reason stored? Data-state assertion for dismissal reason persistence is excluded from Expected Results pending Q-6 resolution.

### Automation Candidate
Yes — core lifecycle flow; suitable for regression once Q-6 is resolved for dismissal storage assertion.

---

## TC-007 — Supervisor Initiates Merge — Non-Survivor Set to Merged, Downstream Event Emitted [CONSTRAINED]

- **Requirement:** US-042 — AC-5: Supervisor completes merge; non-survivor set to Merged; downstream systems notified.
- **Objective:** Verify that a Supervisor can complete a merge, that the non-survivor record transitions to Merged status and is linked to the survivor, and that a downstream notification event is emitted (verified via stub).
- **Priority:** P1-Critical
- **Test Type:** Lifecycle
- **Confidence:** [INFERRED]
- **Related Business Rules:** BR-032 — Merge Requires Supervisor Authorization, BR-033 — Merge Designates One Survivor, BR-034 — Merge is Irreversible, BR-035 — Non-Survivor Retained for Audit, BR-037 — Downstream Systems Notified on Merge, BR-043 — All Changes Produce Audit Entries
- **Related Limitations:** LIM-015 — Merge Cannot Be Partially Reversed, LIM-016 — Merge Does Not Automatically Resolve Data Conflicts, LIM-024 — Downstream Systems Are Notified Asynchronously, LIM-030 — Test Environments Do Not Receive Live Downstream Events
- **Preconditions:**
  1. A Pending customer record (CUST-FLAGGED) exists with an open Duplicate Flag.
  2. An existing Active customer record (CUST-SURVIVOR) is identified as the matching record.
  3. The acting user has Supervisor role and is authenticated.
  4. The test environment downstream stub is configured and listening for merge events (LIM-030).
- **Test Data:**
  - `non_survivor_customer_id`: CUST-FLAGGED
  - `survivor_customer_id`: CUST-SURVIVOR (Active record)
  - `merge_notes`: `Confirmed duplicate — same individual; existing Active record retained as survivor` — optional field, 0–2000 chars (data-model.md Section 7)

### Steps
1. Log in as a user with Supervisor role.
2. Open CUST-FLAGGED (flagged Pending record).
3. Initiate a merge, designating CUST-SURVIVOR as the survivor and CUST-FLAGGED as the non-survivor.
4. Review both records' field values when presented (LIM-016 — system must not auto-resolve conflicts).
5. Confirm the merge.
6. Retrieve CUST-FLAGGED.
7. Retrieve CUST-SURVIVOR.
8. Poll the downstream stub for a merge event (LIM-024 — asynchronous delivery).

### Expected Results

CONSTRAINED — The following assertions are verified:
1. The merge is accepted by the system and a Merge History record is created with `survivor_customer_id = CUST-SURVIVOR` and `non_survivor_customer_id = CUST-FLAGGED` (BR-033; BR-035).
2. CUST-FLAGGED has `status = Merged` after completion (BR-035; AC-5).
3. CUST-FLAGGED has `merged_into = CUST-SURVIVOR.customer_id` (BR-010; BR-035).
4. CUST-SURVIVOR remains Active (or its pre-merge status) (BR-033).
5. A downstream merge event containing both `non_survivor_customer_id` and `survivor_customer_id` is received by the stub system within the polling window (BR-037; AC-5; LIM-024).
6. The stub receives the event asynchronously; no immediate downstream state assertion is made (LIM-024).
7. Audit Events are produced for the merge operation (BR-043).
8. No merge reversal option is presented to the Supervisor after completion (LIM-015).

The following assertions are excluded:
- Whether CUST-FLAGGED (a Pending record) may validly transition to Merged status is unresolved — Q-5 (Pending → Merged absent from BR-016 matrix); this test uses CUST-FLAGGED as the non-survivor and asserts the outcome behaviourally, but the transition validity assertion is CONSTRAINED pending Q-5.
- Survivor designation constraints (whether the Supervisor may designate CUST-FLAGGED as survivor instead) are excluded pending Q-2.

Related limitations: LIM-015, LIM-016, LIM-024, LIM-030.

### Assumptions
- [INFERRED]: The existing Active record is designated the survivor as the most likely valid path; Q-2 has not confirmed whether the Pending record may be the survivor.
- [UNCERTAIN]: Pending → Merged transition validity is unconfirmed (Q-5; A-6 in handoff is Unverified).

### Open Questions
- Q-2: Survivor designation constraint — whether either record may be survivor is unresolved; test uses Active record as survivor.
- Q-5: Pending → Merged transition absent from BR-016 matrix; transition validity assertion is excluded.

### Automation Candidate
Blocked — automation cannot be finalised until Q-2 and Q-5 are resolved and stub polling mechanism is specified.

---

## TC-008 — Supervisor Opens Flagged Record — Comparison View Displayed [CONSTRAINED]

- **Requirement:** US-042 — AC-3: Supervisor opens flagged Pending record; system displays matching records alongside for comparison.
- **Objective:** Verify that when a Supervisor opens a Pending record with an open Duplicate Flag, the system displays the matching record(s) alongside the flagged record in the comparison view; verify that non-restricted fields are visible; field-completeness assertions are constrained by Q-3.
- **Priority:** P2-High
- **Test Type:** Permission
- **Confidence:** [INFERRED]
- **Related Business Rules:** BR-008 — National ID Field Restricted, BR-038 — Role-Based Access Enforcement, BR-039 — Restricted Fields Require Elevated Role
- **Related Limitations:** None.
- **Preconditions:**
  1. A Pending customer record (CUST-FLAGGED) exists with an open Duplicate Flag.
  2. At least one matching record (CUST-MATCH) exists and was identified during duplicate detection.
  3. The acting user has Supervisor role and is authenticated.
- **Test Data:**
  - `customer_id`: CUST-FLAGGED (Pending, open Duplicate Flag)

### Steps
1. Log in as a user with Supervisor role.
2. Open CUST-FLAGGED via the Duplicate Management view.
3. Observe the comparison view displayed.

### Expected Results

CONSTRAINED — The following assertions are verified:
1. The comparison view is displayed showing CUST-FLAGGED alongside at least one matching record (CUST-MATCH) (AC-3).
2. The Supervisor can see at least `first_name`, `last_name`, `email_address`, and `phone_number` for both records (non-restricted fields per BR-039).
3. The national identifier field, if present on either record, is visible to the Supervisor (BR-008; BR-039 — Supervisor role has access to restricted fields).
4. The view does not raise an authorisation error for a Supervisor (BR-038).

The following assertions are excluded pending resolution of Q-3:
- Whether the comparison view includes a complete, defined minimum field set.
- Whether the layout/ordering of fields in the view meets any specification.
- Whether all fields required by AC-3 for "comparison and review" are present.

Related constraint: Q-3 (comparison view field list unspecified).

### Assumptions
- [INFERRED]: Comparison view corresponds to the Duplicate Management functional area described in application-context.md Section 7 (handoff assumption A-8).

### Open Questions
- Q-3: The specific fields required in the comparison view are not defined; field-completeness assertion is excluded from Expected Results.

### Automation Candidate
Blocked — cannot fully automate field-completeness assertions until Q-3 is resolved.

---

## TC-009 — Duplicate Detection Uses Primary Email Only — Secondary Email Match Does Not Raise Flag [BLOCKED]

- **Requirement:** US-042 — AC-7 / LIM-008: Secondary contact methods must not trigger duplicate detection.
- **Objective:** Verify that when a new customer is created with a primary email that is unique but a secondary email that matches an existing Active customer's email, no Duplicate Flag is raised.
- **Priority:** P2-High
- **Test Type:** Negative
- **Confidence:** [UNCERTAIN]
- **Related Business Rules:** BR-011 — Automatic Duplicate Flagging
- **Related Limitations:** LIM-008 — Secondary Contact Methods Are Not Deduplicated, LIM-031 — Duplicate Detection Sensitivity Is Configurable and Environment-Specific
- **Preconditions:**
  1. An existing Active customer (CUST-A) has a secondary email `shared.secondary@example.com`.
  2. The acting user has Agent role and is authenticated.
  3. Duplicate detection thresholds confirmed in test environment (LIM-031).
- **Test Data:**
  - `customer_type`: `Individual`
  - `first_name`: `Different`
  - `last_name`: `Person`
  - `email_address` (Primary): `different.person@example.com` — unique across Active/Pending records
  - `email_address` (Secondary): `shared.secondary@example.com` — same as CUST-A's secondary email
  - `phone_number` (Primary): `+443333333333` — unique

### Steps
1. Log in as a user with Agent role.
2. Submit a new customer creation request with the test data above.
3. Observe the system response.
4. Retrieve the newly created customer record.

### Expected Results
BLOCKED — Expected result cannot be determined until open question Q-1 is resolved:
"The data model does not define a Duplicate Flag entity or field on the Customer entity. Without knowing the flag's data representation and allowed states, a definitive assertion about whether a flag was raised or absent cannot be made with data-state certainty."

The behavioural assertion (no flag raised because LIM-008 excludes secondary contact methods from detection) is logically grounded by LIM-008 and the requirement Notes section, but data-state verification of flag absence depends on Q-1.

### Assumptions
- [CERTAIN]: LIM-008 explicitly excludes secondary contact methods from duplicate detection; a secondary email match must not trigger a flag.
- [UNCERTAIN]: The physical assertion ("no flag present on the record") cannot be written without knowing the flag's data representation (Q-1).

### Open Questions
- Q-1: Duplicate Flag data representation is undefined in the data model. Flag-absence assertion cannot be written definitively until Q-1 is resolved.

### Automation Candidate
Blocked — cannot determine the assertion to automate until Q-1 is resolved.

---

## TC-010 — Duplicate Detection with National Identifier Present on One Record Only — Behaviour Unconfirmed [BLOCKED]

- **Requirement:** US-042 — AC-7: National identifier used in detection only "when provided on both records being compared."
- **Objective:** Verify the system's behaviour when a new customer record includes a national identifier that matches an existing record, but the existing record has no national identifier — specifically, whether this comparison is skipped or treated as a non-match.
- **Priority:** P2-High
- **Test Type:** Data Validation
- **Confidence:** [UNCERTAIN]
- **Related Business Rules:** BR-008 — National ID Field Restricted, BR-009 — One Record Per Verified Identity, BR-011 — Automatic Duplicate Flagging
- **Related Limitations:** LIM-007 — National Identifier Format Validation Is Country-Specific, LIM-031 — Duplicate Detection Sensitivity Is Configurable and Environment-Specific
- **Preconditions:**
  1. An existing Active customer (CUST-B) has `first_name = Same`, `last_name = Person`, primary email `same.person@example.com`, and **no national identifier**.
  2. The acting user has Agent role and is authenticated.
  3. The test environment has national identifier format validation configured for the relevant country (LIM-007).
  4. Duplicate detection thresholds confirmed (LIM-031).
- **Test Data:**
  - `customer_type`: `Individual`
  - `first_name`: `Same`
  - `last_name`: `Person`
  - `email_address` (Primary): `same.person.new@example.com` — unique (to isolate national identifier as the variable)
  - `phone_number` (Primary): `+444444444444` — unique
  - `national_identifier`: `AB12345` — 7 alphanumeric chars, within 5–20 limit (data-model.md Section 1); not held by CUST-B

### Steps
1. Log in as a user with Agent role.
2. Submit a new customer creation request with the test data above.
3. Observe the system response and whether a Duplicate Flag is raised.

### Expected Results
BLOCKED — Expected result cannot be determined until open question Q-4 is resolved:
"When only one of the two records being compared has a national identifier, should the system skip national identifier comparison for that pair, or treat the missing value as a non-match that reduces the overall similarity score? The outcome of this test (flag raised or not) depends entirely on which behaviour is implemented."

### Assumptions
- [UNCERTAIN]: AC-7 states national identifier is used "when provided on both records" — but "skip" vs "treat as non-match" is unresolved (Q-4).

### Open Questions
- Q-4: One-sided national identifier comparison behaviour is unspecified; expected result cannot be determined without resolution.

### Automation Candidate
Blocked — expected result is undetermined until Q-4 is resolved.

---

## Validation Handoff Package

```yaml
schema_version: "1.0"
poc_mode: true
max_test_count: 10
total_tests: 10
ready_count: 6
constrained_count: 2
blocked_count: 2

included_acceptance_criteria:
  - AC-1
  - AC-2
  - AC-3
  - AC-4
  - AC-5
  - AC-6
  - AC-7
  - AC-8

deferred_coverage:
  - area: "Boundary"
    reason: "POC subset — full boundary matrix for first_name (1, 100, 101 chars), last_name (1, 150, 151 chars), national_identifier (4, 5, 20, 21 chars), email (254, 255 chars), phone E.164 not generated; deferred to full run."
  - area: "Concurrency"
    reason: "POC subset — BR-036/LIM-028 concurrent merge serialisation scenario not generated; deferred to full run."
  - area: "Audit"
    reason: "POC subset — dedicated audit-event content and immutability tests (flag creation audit, merge audit field verification, audit cannot be deleted) not generated as standalone tests; deferred to full run."
  - area: "Data Validation — Dismissal Without Reason"
    reason: "POC subset — test for Supervisor attempting dismissal without a written reason (BR-014 rejection) not generated; deferred to full run."
  - area: "Integration — Downstream Failure Path"
    reason: "POC subset — test asserting portal action succeeds when downstream stub does not acknowledge event (LIM-024) not generated as standalone test; deferred to full run."
  - area: "Permission — Viewer Role"
    reason: "POC subset — Viewer role rejection tests for all AC actions not generated; deferred to full run."

open_questions_referenced:
  - Q-1
  - Q-2
  - Q-3
  - Q-4
  - Q-5
  - Q-6

test_cases:
  - test_id: TC-001
    status: READY
  - test_id: TC-002
    status: READY
  - test_id: TC-003
    status: READY
  - test_id: TC-004
    status: READY
  - test_id: TC-005
    status: READY
  - test_id: TC-006
    status: READY
  - test_id: TC-007
    status: CONSTRAINED
  - test_id: TC-008
    status: CONSTRAINED
  - test_id: TC-009
    status: BLOCKED
  - test_id: TC-010
    status: BLOCKED
```