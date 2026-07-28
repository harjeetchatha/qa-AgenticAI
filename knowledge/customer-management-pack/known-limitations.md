# Known Limitations — Customer Management Portal

> **AI Agent Note:** This document records intentional constraints, design boundaries, and operating assumptions of the Customer Management Portal. These are not defects and are not scheduled for change. Use this document when analyzing requirements to identify scope boundaries, when generating tests to avoid scenarios the system is not designed to handle, and when validating outputs to ensure generated test cases do not expect behaviour that is outside the system's defined remit. Where a limitation conflicts with a stated requirement, flag it for human review rather than generating tests against unsupported behaviour.

---

## Limitation Reference Index

| ID | Title | Section |
|---|---|---|
| LIM-001 | No Self-Service Customer Access | Functional |
| LIM-002 | Customer Type Cannot Be Changed After Creation | Functional |
| LIM-003 | Closure Cannot Be Reversed | Functional |
| LIM-004 | No Bulk Customer Creation | Functional |
| LIM-005 | Reason Code List Is Centrally Managed | Functional |
| LIM-006 | No Partial Suspension | Functional |
| LIM-007 | National Identifier Format Validation Is Country-Specific | Data |
| LIM-008 | Secondary Contact Methods Are Not Deduplicated | Data |
| LIM-009 | Address Data Is Not Validated Against External Address Registers | Data |
| LIM-010 | Free-Text Fields Are Not Spell-Checked or Standardised | Data |
| LIM-011 | Search Does Not Support Full-Text or Fuzzy Matching Across All Fields | Search |
| LIM-012 | Closed and Merged Records Require an Explicit Filter to Appear in Search | Search |
| LIM-013 | Search Results Are Bounded by Region for Agent and Viewer Roles | Search |
| LIM-014 | Search Cannot Be Sorted by All Fields | Search |
| LIM-015 | Merge Cannot Be Partially Reversed | Merge |
| LIM-016 | Merge Does Not Automatically Resolve Data Conflicts | Merge |
| LIM-017 | Only Two Records Can Be Merged in a Single Operation | Merge |
| LIM-018 | No Multi-Factor Authentication Is Managed Within the Portal | Security |
| LIM-019 | Custom Roles Are Not Supported | Security |
| LIM-020 | API Credentials Are Not Rotated Automatically | Security |
| LIM-021 | Reports Cannot Be Scheduled Within the Portal | Reporting |
| LIM-022 | Reporting Operates on Snapshots, Not Live Data | Reporting |
| LIM-023 | Audit Log Is Not Searchable in Real Time by All Roles | Reporting |
| LIM-024 | Downstream Systems Are Notified Asynchronously | Integration |
| LIM-025 | The Portal Does Not Read Back Data from Downstream Systems in Real Time | Integration |
| LIM-026 | Integration Contracts Are Fixed Per System | Integration |
| LIM-027 | Search Performance Degrades Beyond Configured Result Thresholds | Performance |
| LIM-028 | Concurrent Merge Operations Are Serialised | Performance |
| LIM-029 | Audit Log Volume Is Not Bounded | Performance |
| LIM-030 | Test Environments Do Not Receive Live Downstream Events | Testing |
| LIM-031 | Duplicate Detection Sensitivity Is Configurable and Environment-Specific | Testing |
| LIM-032 | Consent History Cannot Be Seeded Retrospectively in Test Environments | Testing |

---

## 1. Functional Limitations

---

### LIM-001 — No Self-Service Customer Access

**Description:** End customers (members of the public) do not have direct access to the Customer Management Portal. All record creation, editing, and lifecycle management is performed by internal staff or authorised system integrations. There is no customer-facing portal, API, or login.

**Business Rationale:** The portal is an internal operations tool. Customer-facing self-service is handled by separate applications outside this system's scope.

**Impact on Testing:** Do not generate test scenarios that assume a customer can view, edit, or request deletion of their own record through this portal. Tests for subject access requests or right-to-erasure workflows belong to external systems, not this portal.

**Related Business Rules:** BR-003

---

### LIM-002 — Customer Type Cannot Be Changed After Creation

**Description:** Once a customer record is created as `Individual` or `Organisation`, the `customer_type` field is immutable. It cannot be updated by any user role, including Administrator.

**Business Rationale:** Customer type determines which fields are mandatory, how identity is verified, and how the record is processed downstream. Changing type post-creation would invalidate the existing data model and require complex downstream reconciliation.

**Impact on Testing:** Do not generate tests expecting a type-change update to succeed. Generate negative tests verifying that an attempt to change `customer_type` on an existing record is rejected regardless of role.

**Related Business Rules:** BR-001

---

### LIM-003 — Closure Cannot Be Reversed

**Description:** A customer record in `Closed` status cannot be transitioned to any other status. There is no reopen or reactivation path for a Closed record. If a closed customer needs to be managed again, a new customer record must be created.

**Business Rationale:** Closure represents a deliberate, audited termination of a business relationship. Reversing it would compromise the integrity of the closure record and create ambiguity in historical reporting and downstream systems.

**Impact on Testing:** Generate tests confirming that all status transitions from `Closed` are rejected for every role. Do not generate reopen or reactivation tests for Closed records. Ensure downstream notification tests account for the permanent nature of closure.

**Related Business Rules:** BR-016, BR-019

---

### LIM-004 — No Bulk Customer Creation

**Description:** The portal does not support creating multiple customer records in a single operation. Each customer record must be created individually, either through the portal or via a single-record API call.

**Business Rationale:** Individual record creation enforces per-record duplicate detection, validation, and audit logging. Bulk creation would bypass these controls and is not a supported operational workflow.

**Impact on Testing:** Do not generate test scenarios for batch or bulk creation through the portal. Volume testing of the creation flow must use sequential individual calls rather than a bulk import mechanism.

**Related Business Rules:** BR-004, BR-011

---

### LIM-005 — Reason Code List Is Centrally Managed

**Description:** The list of valid reason codes for suspension and closure transitions is maintained by Administrators through system configuration. It is not user-editable during a status transition. If a required reason code does not exist in the configured list, the transition cannot be completed until the list is updated by an Administrator.

**Business Rationale:** Centralised management of reason codes ensures consistency in reporting and downstream handling. Ad-hoc reason entry would produce unclassifiable data.

**Impact on Testing:** Tests requiring specific reason codes must verify those codes exist in the environment's configuration before execution. Do not assume a specific reason code value is present in all environments. Negative tests should verify that values not in the configured list are rejected.

**Related Business Rules:** BR-018

---

### LIM-006 — No Partial Suspension

**Description:** Suspension applies to the entire customer record. The portal does not support suspending a customer for one channel, product, or region while leaving them active in others. Suspension is an all-or-nothing account-level status.

**Business Rationale:** The Customer Management Portal manages customer identity and lifecycle only. Channel- or product-specific restrictions are governed by downstream systems (e.g., the billing or communications platform), not this portal.

**Impact on Testing:** Do not generate tests expecting channel-specific or product-specific suspension behaviour. Tests for partial access restriction should target downstream systems, not this portal.

**Related Business Rules:** BR-016, BR-018

---

## 2. Data Limitations

---

### LIM-007 — National Identifier Format Validation Is Country-Specific

**Description:** The system validates the format of a national identifier (e.g., tax ID, NI number) based on the customer's associated country. If no country context is available or the country's format rules are not configured, format validation is not applied. The system does not verify the identifier's authenticity against any external government register.

**Business Rationale:** National identifier formats differ significantly by country. External verification against government registers is outside the system's scope and involves regulatory and technical constraints.

**Impact on Testing:** Test national identifier validation only for countries whose format rules are configured in the test environment. Do not generate tests expecting real-time government verification. Generate tests for unconfigured country codes to confirm that validation is gracefully bypassed.

**Related Business Rules:** BR-008, BR-009

---

### LIM-008 — Secondary Contact Methods Are Not Deduplicated

**Description:** Uniqueness constraints on email and phone apply only to `Primary` contact methods. Secondary email addresses and secondary phone numbers can be shared across multiple customer records without triggering a duplicate flag.

**Business Rationale:** Secondary contact details are supplementary. They may legitimately be shared (e.g., a company switchboard number used by multiple contacts). Deduplication at the secondary level would produce excessive false-positive flags.

**Impact on Testing:** Do not generate duplicate detection tests using secondary contact methods. Uniqueness constraint tests must use primary contact methods only. Confirm that adding a duplicate secondary email does not raise a flag.

**Related Business Rules:** BR-002, BR-026

---

### LIM-009 — Address Data Is Not Validated Against External Address Registers

**Description:** The system validates address fields for format completeness (e.g., postcode format against country code) but does not verify that the address physically exists or is correctly formatted according to an external address register or postal authority database.

**Business Rationale:** Real-time address verification introduces dependency on third-party services and creates latency and availability risks. Address quality is managed through operational processes, not system-level validation.

**Impact on Testing:** Do not generate tests expecting an address to be rejected because it does not exist in the real world. Postcode format tests should focus on structural format compliance only. Boundary tests should use structurally valid but fictitious addresses.

**Related Business Rules:** BR-047

---

### LIM-010 — Free-Text Fields Are Not Spell-Checked or Standardised

**Description:** Free-text fields such as notes, organisation names, and address lines are stored exactly as entered. The system does not apply spell-checking, name standardisation, or auto-correction. Inconsistent data entry (e.g., "Smith" vs "SMITH" vs "smith") is not flagged or resolved automatically.

**Business Rationale:** Automated standardisation of free-text fields risks modifying legally significant data (e.g., registered business names). Standardisation is a data quality process owned by operations teams, not a system function.

**Impact on Testing:** Do not generate tests expecting automatic capitalisation, name normalisation, or spell correction. Duplicate detection tests that rely on name matching should account for the configurable matching sensitivity rather than expecting exact-match-only behaviour.

**Related Business Rules:** BR-011, BR-048

---

## 3. Search Limitations

---

### LIM-011 — Search Does Not Support Full-Text or Fuzzy Matching Across All Fields

**Description:** Customer search supports matching on a defined set of indexed fields (name, primary email, primary phone, customer ID, national identifier). It does not support full-text search across notes, address lines, or audit content. Fuzzy matching (e.g., phonetic or edit-distance matching) is applied only to name fields during duplicate detection, not general search.

**Business Rationale:** Full-text search across all fields is computationally expensive at the data volumes anticipated. Fuzzy search for general queries produces excessive false positives.

**Impact on Testing:** Do not generate search tests expecting results from notes or unindexed fields. Fuzzy-match behaviour should only be tested in the context of duplicate detection, not customer search.

**Related Business Rules:** BR-029

---

### LIM-012 — Closed and Merged Records Require an Explicit Filter to Appear in Search

**Description:** Default search queries exclude records with `Closed` or `Merged` status. These records are only returned when a user explicitly applies a status filter to include them. This behaviour cannot be overridden by any user role.

**Business Rationale:** Operational search results should reflect the active customer base. Including historical records by default increases noise and the risk of staff acting on the wrong record.

**Impact on Testing:** Verify that Closed and Merged records do not appear in default searches even when search terms match exactly. Generate separate tests for filtered searches that include these statuses. Do not assume that any user role can change the default exclusion behaviour.

**Related Business Rules:** BR-028

---

### LIM-013 — Search Results Are Bounded by Region for Agent and Viewer Roles

**Description:** Users with Agent or Viewer roles can only retrieve records assigned to their configured region, regardless of the search term used. A direct lookup by Customer ID for an out-of-region record returns no result for these roles.

**Business Rationale:** Regional data access boundaries are a governance control. Out-of-region access is a data privacy risk.

**Impact on Testing:** Tests for region-bounded access must verify that even exact ID lookups return no result for out-of-region records. Do not assume that knowing a Customer ID grants access to the record. Cross-region access tests should confirm success only for Supervisor and Administrator roles.

**Related Business Rules:** BR-031, BR-038

---

### LIM-014 — Search Cannot Be Sorted by All Fields

**Description:** Search results can be sorted only by a predefined set of fields (e.g., last name, created date, status). Sorting by notes content, audit data, address fields, or consent history is not supported.

**Business Rationale:** Sorting is supported only on indexed fields for performance reasons. Sorting on non-indexed fields at scale would cause unacceptable query times.

**Impact on Testing:** Do not generate tests for sort operations on unsupported fields. Confirm that unsupported sort parameters are either rejected or silently ignored according to the defined API contract. Sort tests should cover ascending and descending order on each supported field only.

**Related Business Rules:** BR-030

---

## 4. Merge Limitations

---

### LIM-015 — Merge Cannot Be Partially Reversed

**Description:** Once a merge is confirmed and completed, it cannot be undone through any portal function. Reversal requires a manual data remediation process executed outside the application, typically involving a data engineering team.

**Business Rationale:** The merge event has been propagated to all downstream systems. Automated reversal would require compensating transactions across every integrated system in a guaranteed-delivery manner, which is not architecturally supported.

**Impact on Testing:** Do not generate tests expecting a merge reversal function. Generate tests confirming that no reversal option is exposed to any user role. Negative tests should verify that the non-survivor remains in `Merged` status after the operation completes.

**Related Business Rules:** BR-034

---

### LIM-016 — Merge Does Not Automatically Resolve Data Conflicts

**Description:** When two records are merged, the system does not automatically choose which field values from the non-survivor to apply to the survivor. A Supervisor must explicitly select which non-survivor fields, if any, to carry over. No field is automatically overwritten.

**Business Rationale:** Automated field resolution rules would be arbitrary and could overwrite correct data with incorrect data. The Supervisor reviewing the merge has the context to make this decision correctly.

**Impact on Testing:** Do not generate tests expecting automatic field merging or conflict resolution. Tests should confirm that the Supervisor is presented with both records' field values for selective application before confirmation. Verify that the survivor's fields remain unchanged if no field selection is made by the Supervisor.

**Related Business Rules:** BR-033

---

### LIM-017 — Only Two Records Can Be Merged in a Single Operation

**Description:** A merge operation combines exactly two customer records: one Survivor and one Non-Survivor. Merging three or more records into a single canonical record requires sequential merge operations — first merging two, then merging the survivor with the third.

**Business Rationale:** Three-way or n-way merges significantly increase the complexity of conflict resolution, audit logging, and downstream notification. Two-record merges are the supported unit of work.

**Impact on Testing:** Do not generate tests for multi-record merges in a single operation. Generate sequential merge tests when a three-or-more-record consolidation scenario is required. Verify that submitting three record IDs in a single merge request is rejected.

**Related Business Rules:** BR-032, BR-033, BR-036

---

## 5. Security Limitations

---

### LIM-018 — No Multi-Factor Authentication Is Managed Within the Portal

**Description:** The portal delegates all authentication, including multi-factor authentication, to the external Identity Provider (IdP) via SSO. The portal itself does not implement, enforce, or configure MFA. MFA policy is owned by the IdP configuration, not this application.

**Business Rationale:** Centralised authentication management through an IdP avoids credential sprawl and ensures consistent security policy across all internal applications.

**Impact on Testing:** Do not generate MFA test scenarios for the portal itself. Authentication strength tests belong to the IdP test suite. Portal security tests should focus on authorisation (role enforcement, field access) rather than authentication mechanisms.

**Related Business Rules:** BR-040

---

### LIM-019 — Custom Roles Are Not Supported

**Description:** The portal supports exactly five roles: Viewer, Agent, Supervisor, Administrator, and System. Custom roles with individually configured permissions cannot be created. Role capabilities are fixed and cannot be modified by any user, including Administrators.

**Business Rationale:** Fixed roles simplify authorisation logic, auditability, and onboarding. Custom roles increase the attack surface for privilege misconfiguration.

**Impact on Testing:** Do not generate tests for custom role creation or per-user permission overrides. Permission boundary tests must be structured around the five defined roles only. Do not test for permission inheritance or role stacking.

**Related Business Rules:** BR-038, BR-042

---

### LIM-020 — API Credentials Are Not Rotated Automatically

**Description:** API credentials issued to integration systems do not rotate automatically on a schedule. Credential rotation must be triggered manually by an Administrator. Expired credentials cause integration failures until renewed.

**Business Rationale:** Automated credential rotation requires integration with each downstream system's credential store, which is outside this portal's scope. Rotation is managed as part of each integration's operational runbook.

**Impact on Testing:** Integration tests that depend on API credentials must account for manual credential management in test environments. Do not assume credentials are always valid; include test setup steps to verify credential validity. Tests for expired-credential behaviour should be run against a deliberately expired credential, not an automatically cycled one.

**Related Business Rules:** BR-041

---

## 6. Reporting Limitations

---

### LIM-021 — Reports Cannot Be Scheduled Within the Portal

**Description:** The portal does not provide a built-in report scheduling or subscription mechanism. Reports are generated on demand only. Scheduled reporting is the responsibility of the Data Warehouse or an external reporting platform that consumes portal data.

**Business Rationale:** Scheduled reporting at scale is a data platform concern. Embedding scheduling in the portal would duplicate functionality owned by the data warehouse layer.

**Impact on Testing:** Do not generate tests for scheduled report delivery, email distribution of reports, or automated report generation. Report tests should cover on-demand generation, filter correctness, and result accuracy only.

**Related Business Rules:** BR-054, BR-055

---

### LIM-022 — Reporting Operates on Snapshots, Not Live Data

**Description:** All reports are generated against a declared point-in-time snapshot of customer data rather than a live query. The snapshot is taken at the moment the report is requested. Data changes made after the snapshot is taken are not reflected in the report.

**Business Rationale:** Live queries across large datasets during report generation would produce internally inconsistent results as records change during the query window. Snapshots guarantee internal consistency within a single report.

**Impact on Testing:** Generate tests that verify reports do not change once generated, even if underlying data changes after generation. Do not expect a re-run of the same report parameters to produce identical results if data has changed between runs.

**Related Business Rules:** BR-055

---

### LIM-023 — Audit Log Is Not Searchable in Real Time by All Roles

**Description:** The full audit log is accessible only to users with Administrator role. Supervisors can view the audit history for specific customer records they are authorised to access. Agents and Viewers cannot query the audit log. Keyword or cross-record audit search is restricted to Administrators.

**Business Rationale:** The audit log contains sensitive field-level change data, including old and new values of restricted fields. Broad access to the audit log is a data governance risk. Operational users have access to the customer record itself; audit log access is a compliance function.

**Impact on Testing:** Verify that Agents and Viewers receive an authorisation error when attempting to access the audit log. Verify that Supervisors can view the audit history for records within their region but cannot perform cross-record audit queries. Full audit log search tests must use Administrator credentials.

**Related Business Rules:** BR-043, BR-044, BR-046

---

## 7. Integration Limitations

---

### LIM-024 — Downstream Systems Are Notified Asynchronously

**Description:** When a customer status changes or a merge is completed, downstream systems (billing, communications, case management, data warehouse) are notified via an asynchronous event mechanism. The portal does not wait for downstream acknowledgement before confirming the action to the user. Downstream processing lag is expected and by design.

**Business Rationale:** Synchronous downstream notification would make portal response times dependent on the availability and performance of every integrated system, creating unacceptable coupling.

**Impact on Testing:** Do not generate tests that assert an immediate downstream state change following a portal action. Integration tests must account for processing lag and use polling or event-listening mechanisms to verify downstream state. Downstream failure tests should confirm the portal action succeeds while the notification is queued for retry.

**Related Business Rules:** BR-022, BR-037

---

### LIM-025 — The Portal Does Not Read Back Data from Downstream Systems in Real Time

**Description:** The portal does not query downstream systems (e.g., billing, case management) in real time to display balance, case status, or product information. It reads closure pre-conditions (open cases, outstanding balance) via a point-in-time check at the moment a closure is initiated. This data is not continuously refreshed.

**Business Rationale:** Real-time integration with multiple downstream systems at every page load would introduce latency and availability dependencies unacceptable for an operational portal.

**Impact on Testing:** Do not test that the portal displays live billing balances or case counts. Closure pre-condition tests must verify the check is executed at closure initiation time. Tests that require a specific downstream state (e.g., no open cases) must set that state directly in the downstream system before triggering the portal action.

**Related Business Rules:** BR-017

---

### LIM-026 — Integration Contracts Are Fixed Per System

**Description:** The data format, authentication method, and event schema exchanged between the Customer Management Portal and each downstream system are defined in a fixed integration contract agreed between teams. The portal cannot dynamically adapt its outbound events to suit downstream system changes without a contract renegotiation and deployment.

**Business Rationale:** Stable integration contracts protect downstream teams from unexpected breaking changes. Contract changes require coordination across system owners.

**Impact on Testing:** Do not generate tests expecting dynamic or configurable event formats. Integration tests should validate that outbound events conform to the current contract schema. When a contract changes, integration tests must be updated to reflect the new agreed schema.

**Related Business Rules:** BR-022, BR-037, BR-041

---

## 8. Performance Assumptions

---

### LIM-027 — Search Performance Degrades Beyond Configured Result Thresholds

**Description:** The search engine is optimised for queries returning up to the configured maximum result set size (default: 500 records across pages). Queries that would return very large result sets are automatically capped. Performance and response times are not guaranteed for queries approaching or exceeding this threshold.

**Business Rationale:** The portal is an operational tool used for targeted lookup. Mass data extraction is a data warehouse function. Capping results protects system performance for all concurrent users.

**Impact on Testing:** Performance tests must use targeted queries representative of real operational use. Do not run performance baselines using deliberately broad search terms designed to return maximum results. Boundary tests should verify that the cap is enforced and that a meaningful message is returned when results are truncated.

**Related Business Rules:** BR-029, BR-030

---

### LIM-028 — Concurrent Merge Operations Are Serialised

**Description:** When two Supervisors attempt to initiate a merge involving the same customer record simultaneously, the second request is queued and will fail if the first merge is still in progress. Concurrent merges on the same record are not supported and the second operation returns a conflict error.

**Business Rationale:** Concurrent merges on the same record create race conditions with indeterminate outcomes. Serialisation guarantees a consistent result.

**Impact on Testing:** Concurrency tests should verify that the second merge request for the same record returns a clear conflict error, not a silent failure or data corruption. Do not generate tests expecting parallel merge operations on the same record to succeed. Tests for concurrent merges on different records should proceed independently.

**Related Business Rules:** BR-036, BR-053

---

### LIM-029 — Audit Log Volume Is Not Bounded

**Description:** Audit log records are retained indefinitely and are never purged. Over time, the volume of audit data will grow continuously. Query performance against the audit log is not guaranteed for full-history queries on high-activity customer records.

**Business Rationale:** Indefinite retention is a compliance requirement (BR-046). Bounding or purging audit data would breach regulatory obligations.

**Impact on Testing:** Audit log retrieval tests should be scoped to specific customer records or time windows, not full-log queries. Performance tests for audit log access should use representative data volumes for the target environment. Do not design tests that assume fast full-audit-log retrieval in production-sized environments.

**Related Business Rules:** BR-046

---

## 9. Testing Considerations

---

### LIM-030 — Test Environments Do Not Receive Live Downstream Events

**Description:** Test and staging environments are isolated from production downstream systems. Downstream event notifications (billing, communications, case management) sent from a test environment are routed to stub or mock systems, not live downstream environments. Test environments cannot verify real downstream processing outcomes.

**Business Rationale:** Sending test events to live downstream systems would corrupt production data and trigger real operational processes (e.g., billing runs, customer communications).

**Impact on Testing:** Integration tests in non-production environments must use downstream stubs or contract test frameworks. Tests that assert downstream state must use the stub system's API to verify event receipt. Full end-to-end integration testing spanning real downstream systems is a production-only activity requiring strict change controls.

**Related Business Rules:** BR-022, BR-037

---

### LIM-031 — Duplicate Detection Sensitivity Is Configurable and Environment-Specific

**Description:** The duplicate detection matching algorithm uses configurable thresholds (e.g., name similarity score, field weights). These thresholds may differ between environments (development, staging, production). A test that passes duplicate detection in one environment may be flagged in another if thresholds are configured differently.

**Business Rationale:** Duplicate detection sensitivity must be tunable to balance false-positive flags against missed duplicates. The appropriate threshold depends on data quality characteristics that may differ by environment.

**Impact on Testing:** Duplicate detection tests must document the expected configuration thresholds and verify those thresholds are set correctly before execution. Tests should not assume uniform duplicate detection behaviour across all environments. Environment-specific threshold values should be documented in test setup preconditions.

**Related Business Rules:** BR-011, BR-012

---

### LIM-032 — Consent History Cannot Be Seeded Retrospectively in Test Environments

**Description:** Because consent records are versioned and immutable, it is not possible to backdate or inject historical consent records with past timestamps through the portal's standard interfaces. Test scenarios requiring a specific consent history must build that history forward in time through sequential consent operations in the test environment.

**Business Rationale:** Backdating consent records would undermine the integrity of the consent audit trail, which is a regulatory compliance requirement.

**Impact on Testing:** Test cases requiring multi-version consent history must be executed sequentially to build the history organically. Do not design tests that require injecting pre-built consent history unless the test environment provides a dedicated data seeding utility that operates outside the standard application flow. Document the required consent history build-up as explicit precondition steps in the test design.

**Related Business Rules:** BR-045, BR-046
