# Business Rules — Customer Management Portal

> **AI Agent Note:** This document defines the business rules governing the Customer Management Portal. Use it to map requirements to affected rules, identify rule conflicts, derive test conditions, and generate boundary and negative test scenarios. Rules are authoritative. Where a requirement conflicts with a rule, flag it for human review.

---

## Rule Reference Index

| ID | Title | Section |
|---|---|---|
| BR-001 | Mandatory Fields on Creation | Customer Creation |
| BR-002 | Unique Email on Creation | Customer Creation |
| BR-003 | Agent Role Required for Creation | Customer Creation |
| BR-004 | Duplicate Check Before Activation | Customer Creation |
| BR-005 | System-Generated Customer ID | Customer Creation |
| BR-006 | Initial Status is Pending | Customer Creation |
| BR-007 | Customer ID Immutability | Customer Identification |
| BR-008 | National ID Field Restricted | Customer Identification |
| BR-009 | One Record Per Verified Identity | Customer Identification |
| BR-010 | Merged Record Reference | Customer Identification |
| BR-011 | Automatic Duplicate Flagging | Duplicate Detection |
| BR-012 | Duplicate Flag on Update | Duplicate Detection |
| BR-013 | Manual Duplicate Check Trigger | Duplicate Detection |
| BR-014 | Duplicate Dismissal Requires Authorization | Duplicate Detection |
| BR-015 | Duplicate Flag Blocks Activation | Duplicate Detection |
| BR-016 | Allowed Status Transitions | Customer Status |
| BR-017 | Closure Requires No Open Obligations | Customer Status |
| BR-018 | Suspension Requires Reason Code | Customer Status |
| BR-019 | Closed Status is Terminal | Customer Status |
| BR-020 | Reactivation Requires Supervisor | Customer Status |
| BR-021 | Suspended Customer is Read-Only for Agents | Customer Status |
| BR-022 | Status Change Propagated to Downstream | Customer Status |
| BR-023 | At Least One Verified Contact Method | Contact Information |
| BR-024 | Email Format Validation | Contact Information |
| BR-025 | Phone Number Format Validation | Contact Information |
| BR-026 | Contact Method Uniqueness | Contact Information |
| BR-027 | Consent Flag Required for Communications | Contact Information |
| BR-028 | Default Search Excludes Closed and Merged | Search |
| BR-029 | Minimum Search Term Length | Search |
| BR-030 | Search Results are Paginated | Search |
| BR-031 | Search Scope Bounded by Role | Search |
| BR-032 | Merge Requires Supervisor Authorization | Merge |
| BR-033 | Merge Designates One Survivor | Merge |
| BR-034 | Merge is Irreversible | Merge |
| BR-035 | Non-Survivor Retained for Audit | Merge |
| BR-036 | Only One Active Merge Per Record | Merge |
| BR-037 | Downstream Systems Notified on Merge | Merge |
| BR-038 | Role-Based Access Enforcement | Security & Permissions |
| BR-039 | Restricted Fields Require Elevated Role | Security & Permissions |
| BR-040 | Session Timeout Enforces Re-authentication | Security & Permissions |
| BR-041 | API Access Governed by Integration Contract | Security & Permissions |
| BR-042 | Administrator Cannot Self-Assign Permissions | Security & Permissions |
| BR-043 | All Changes Produce Audit Entries | Audit & Compliance |
| BR-044 | Audit Log is Immutable | Audit & Compliance |
| BR-045 | Consent State is Versioned | Audit & Compliance |
| BR-046 | Audit Retention is Indefinite | Audit & Compliance |
| BR-047 | Required Fields Cannot be Blanked | Data Integrity |
| BR-048 | Customer Name Cannot Contain Only Whitespace | Data Integrity |
| BR-049 | Date Fields Must be Chronologically Valid | Data Integrity |
| BR-050 | Referential Integrity for Linked Records | Data Integrity |
| BR-051 | Validation Errors Returned with Field-Level Detail | Error Handling |
| BR-052 | Rejected Transitions Return Business Reason | Error Handling |
| BR-053 | Concurrent Edit Conflict Must Be Detected | Error Handling |
| BR-054 | Closed and Merged Records Excluded from Live Metrics | Reporting |
| BR-055 | Status Distribution Report Reflects Point-in-Time State | Reporting |
| BR-056 | Duplicate Resolution Rate is a Tracked Metric | Reporting |

---

## 1. Customer Creation Rules

---

### BR-001 — Mandatory Fields on Creation

**Rule:** A customer record cannot be created unless the following fields are provided: first name, last name, at least one contact method (email or phone), and customer type (Individual or Organization).

**Rationale:** Incomplete records cannot be used for communication, identification, or downstream processing. Partial records degrade data quality across the system.

**Business Impact if Violated:** Unusable records enter the system, causing failures in billing, communications, and reporting. Downstream systems may reject or mishandle the record.

---

### BR-002 — Unique Email on Creation

**Rule:** No two Active or Pending customer records may share the same primary email address. If a duplicate email is detected, creation is blocked and a duplicate warning is raised.

**Rationale:** Email is the primary channel for customer communication and identity verification. Duplicate emails cause message misrouting and identity confusion.

**Business Impact if Violated:** Customers receive communications intended for others. Billing and case management link to the wrong record.

---

### BR-003 — Agent Role Required for Creation

**Rule:** Only users with the Agent, Supervisor, or Administrator role (or an authorized system integration) may create a new customer record. Viewers may not create records.

**Rationale:** Record creation is a data-entry action requiring accountability. Viewers are read-only consumers.

**Business Impact if Violated:** Unauthorized records enter the system without an accountable owner, introducing integrity and audit risks.

---

### BR-004 — Duplicate Check Before Activation

**Rule:** The system must run duplicate detection before a newly created customer record transitions from Pending to Active. If a potential duplicate is flagged, the transition is blocked until the flag is resolved.

**Rationale:** Activating a record without a duplicate check allows duplicate customers to proliferate. The cost of resolving duplicates post-activation is significantly higher than preventing them at creation.

**Business Impact if Violated:** Duplicate Active records cause split billing histories, conflicting case records, and regulatory non-compliance.

---

### BR-005 — System-Generated Customer ID

**Rule:** The system assigns a unique, immutable customer identifier to every record at the moment of creation. This identifier is not editable by any user role.

**Rationale:** A stable system identifier is required to maintain referential integrity across all linked systems and historical records.

**Business Impact if Violated:** Referential integrity breaks across billing, cases, and audit. Historical linkage is lost.

---

### BR-006 — Initial Status is Pending

**Rule:** All newly created customer records begin in **Pending** status. A record cannot be set directly to Active, Suspended, or Closed at creation.

**Rationale:** Pending status provides a gate for duplicate checks and data validation before a record becomes operational.

**Business Impact if Violated:** Records that have not passed validation checks enter the live system, polluting data and triggering premature downstream events.

---

## 2. Customer Identification Rules

---

### BR-007 — Customer ID Immutability

**Rule:** The system-generated customer ID cannot be changed, transferred, or reused for any reason, including after a merge or closure.

**Rationale:** Downstream systems use the customer ID as a permanent foreign key. Any change breaks historical linkage.

**Business Impact if Violated:** Data integrity across billing, reporting, and case management is permanently broken.

---

### BR-008 — National ID Field Restricted

**Rule:** Fields containing national or government-issued identifiers (e.g., tax ID, national insurance number) are visible and editable only by users with Supervisor or Administrator role.

**Rationale:** These fields are subject to regulatory data handling obligations and must be protected against unauthorized access.

**Business Impact if Violated:** Regulatory breach, potential legal liability, and unauthorized disclosure of personally identifiable information.

---

### BR-009 — One Record Per Verified Identity

**Rule:** No two Active customer records may represent the same verified legal identity. Identity is established by a combination of name, date of birth, and national identifier where provided.

**Rationale:** Duplicate identities cause systemic failures in compliance, credit, and communications.

**Business Impact if Violated:** The organization may extend credit or services to the same person twice, and regulatory reporting will contain duplicate subjects.

---

### BR-010 — Merged Record Reference

**Rule:** When a customer record is merged, the non-surviving record must retain a permanent, visible reference to the surviving record's customer ID.

**Rationale:** The non-surviving record must remain traceable for audit, legal discovery, and historical inquiry purposes.

**Business Impact if Violated:** Historical records become orphaned and untraceable, creating audit gaps and compliance failures.

---

## 3. Duplicate Detection Rules

---

### BR-011 — Automatic Duplicate Flagging

**Rule:** The system must automatically evaluate every new customer record for duplicates against all Active and Pending records at the point of creation, using a configurable matching algorithm (name similarity, email, phone, national identifier).

**Rationale:** Manual duplicate checking is unreliable at scale. Automated detection reduces the rate of duplicate proliferation.

**Business Impact if Violated:** Duplicate records accumulate, increasing resolution costs and degrading data quality over time.

---

### BR-012 — Duplicate Flag on Update

**Rule:** If a contact method (email or phone) on an existing record is updated to a value already held by another Active record, the system must raise a duplicate flag.

**Rationale:** Duplicate records are often created when contact details change and the original record is not found. Checking on update catches this scenario.

**Business Impact if Violated:** A record update silently creates a duplicate contact identifier, causing future communications to misroute.

---

### BR-013 — Manual Duplicate Check Trigger

**Rule:** Any user with Agent role or above may manually trigger a duplicate detection scan on any Active or Pending customer record at any time.

**Rationale:** Duplicate conditions can arise from data changes in other records. Manual triggering allows staff to verify record uniqueness on demand.

**Business Impact if Violated:** Staff cannot proactively identify duplicates, reducing confidence in record uniqueness.

---

### BR-014 — Duplicate Dismissal Requires Authorization

**Rule:** A duplicate flag may only be dismissed (i.e., the record cleared to proceed) by a user with Supervisor role or above. Dismissal must include a written reason.

**Rationale:** Dismissing a duplicate flag is a risk decision. It must be made by an authorized person and documented.

**Business Impact if Violated:** Agents dismiss duplicate flags without oversight, allowing genuine duplicates to become Active records.

---

### BR-015 — Duplicate Flag Blocks Activation

**Rule:** A Pending customer record with an open duplicate flag cannot transition to Active until the flag is either resolved through merge or explicitly dismissed by a Supervisor.

**Rationale:** Activating a potentially duplicate record bypasses the organization's data integrity controls.

**Business Impact if Violated:** Duplicate Active records proliferate, with full operational impact (split billing, duplicate communications, regulatory risk).

---

## 4. Customer Status Rules

---

### BR-016 — Allowed Status Transitions

**Rule:** Customer status may only follow these permitted transitions:

| From | To | Authorized Role |
|---|---|---|
| Pending | Active | Agent+ |
| Pending | Closed | Supervisor+ |
| Active | Suspended | Supervisor+ |
| Active | Closed | Supervisor+ |
| Suspended | Active | Supervisor+ |
| Suspended | Closed | Supervisor+ |

Any transition not listed above must be rejected with a business reason.

**Rationale:** Uncontrolled status changes corrupt the customer lifecycle and generate invalid downstream events.

**Business Impact if Violated:** Customers may be incorrectly billed, communicated with, or reported on based on an invalid status.

---

### BR-017 — Closure Requires No Open Obligations

**Rule:** A customer record cannot be set to Closed if the customer has any open service cases or an outstanding balance in the billing system. The system must validate these conditions before permitting closure.

**Rationale:** Closing a record with open obligations orphans those obligations and removes visibility for the teams managing them.

**Business Impact if Violated:** Open cases and unpaid balances are abandoned. Downstream teams lose access to customer context for resolution.

---

### BR-018 — Suspension Requires Reason Code

**Rule:** When a customer is suspended, a mandatory reason code must be selected from a predefined list. Free-text notes are optional but the reason code is required.

**Rationale:** Reason codes enable consistent reporting, analysis, and downstream system handling of suspensions.

**Business Impact if Violated:** Suspensions cannot be categorized or reported on. Downstream systems cannot determine the appropriate response to the suspension.

---

### BR-019 — Closed Status is Terminal

**Rule:** A Closed customer record cannot be transitioned to any other status. No edits may be made to a Closed record. It is permanently read-only.

**Rationale:** Closure represents a terminated business relationship. Reopening a closed record requires a new customer creation process to maintain data integrity.

**Business Impact if Violated:** Closed records are modified or reactivated, corrupting the historical record and potentially reviving accounts that were closed for compliance reasons.

---

### BR-020 — Reactivation Requires Supervisor

**Rule:** Transitioning a customer from Suspended to Active (reactivation) requires authorization from a user with Supervisor role or above.

**Rationale:** Reactivation reverses a decision that was also made at Supervisor level. It must be subject to the same level of oversight.

**Business Impact if Violated:** Agents reactivate suspended accounts without oversight, potentially restoring accounts that were suspended for fraud or compliance reasons.

---

### BR-021 — Suspended Customer is Read-Only for Agents

**Rule:** Users with Agent role cannot edit any field on a Suspended customer record. They may view the record and add notes, but all field edits require Supervisor authorization.

**Rationale:** Suspended records are under review. Unrestricted edits could interfere with the suspension resolution process.

**Business Impact if Violated:** An Agent edits a suspended record, potentially removing evidence relevant to the suspension cause.

---

### BR-022 — Status Change Propagated to Downstream

**Rule:** Every status change (including Pending→Active, Active→Suspended, and all closure transitions) must generate a system event that notifies all registered downstream systems (billing, communications, case management) within the same transaction or via a guaranteed delivery mechanism.

**Rationale:** Downstream systems rely on customer status to govern their own behavior (e.g., halting billing on suspension). Missed notifications cause operational failures.

**Business Impact if Violated:** A suspended customer continues to be billed. A closed customer continues to receive communications. Downstream systems operate on stale state.

---

## 5. Contact Information Rules

---

### BR-023 — At Least One Verified Contact Method

**Rule:** Every Active customer record must have at least one verified contact method — either a verified email address or a verified phone number. A record cannot be activated or remain Active without one.

**Rationale:** The organization must be able to contact every Active customer. Records without contact methods are operationally useless and may indicate incomplete or fraudulent data.

**Business Impact if Violated:** The organization cannot reach the customer for billing, compliance, or service communications.

---

### BR-024 — Email Format Validation

**Rule:** Any email address stored on a customer record must conform to standard RFC 5321 email format. Malformed email addresses must be rejected at the point of entry.

**Rationale:** Invalid email formats cause communication failures and indicate data entry errors.

**Business Impact if Violated:** Communications fail silently. The customer is unreachable by email without the organization being aware.

---

### BR-025 — Phone Number Format Validation

**Rule:** Phone numbers must be stored in E.164 international format. The system must accept common local formats at input and normalize them to E.164 on save.

**Rationale:** Consistent format enables routing, deduplication, and integration with communications platforms.

**Business Impact if Violated:** Phone numbers stored in inconsistent formats fail deduplication checks and cannot be used by the communications platform.

---

### BR-026 — Contact Method Uniqueness

**Rule:** A primary email address or primary phone number may not be shared between two Active customer records. Secondary contact methods are not subject to this constraint.

**Rationale:** Primary contact methods are used for identity verification and account recovery. Shared values create ambiguity.

**Business Impact if Violated:** Password reset, identity verification, and account communications are routed to the wrong customer.

---

### BR-027 — Consent Flag Required for Communications

**Rule:** The communications platform may only contact a customer if the customer's record carries an explicit, timestamped consent flag for the relevant channel (email, phone, post). Absent or withdrawn consent must block outbound contact on that channel.

**Rationale:** Regulatory requirements (e.g., GDPR, PECR) prohibit unsolicited marketing and some service communications without consent.

**Business Impact if Violated:** Regulatory breach, financial penalties, and reputational damage from unsolicited customer contact.

---

## 6. Search Rules

---

### BR-028 — Default Search Excludes Closed and Merged

**Rule:** Default customer search results must exclude records with a status of Closed or Merged. Users may opt in to include these by applying an explicit filter.

**Rationale:** Closed and merged records are not operationally active. Surfacing them by default increases noise and the likelihood of staff acting on the wrong record.

**Business Impact if Violated:** Staff create updates or actions on closed or non-surviving records, corrupting the system state.

---

### BR-029 — Minimum Search Term Length

**Rule:** A customer search must require a minimum of three characters in any search field. Single or double character queries must be rejected.

**Rationale:** Short search terms produce excessive results volumes, degrading performance and usability.

**Business Impact if Violated:** System performance degrades under broad queries. Staff are presented with unmanageable result sets.

---

### BR-030 — Search Results are Paginated

**Rule:** Search results must be returned in pages of a configurable size (default: 25 records per page). The system must not return an unbounded result set in a single response.

**Rationale:** Unbounded result sets degrade system performance and overwhelm the consuming agent or user.

**Business Impact if Violated:** System timeouts, API failures, and degraded performance for all concurrent users.

---

### BR-031 — Search Scope Bounded by Role

**Rule:** Users with Viewer or Agent role may only search within their assigned region or business unit. Supervisors and Administrators can search across all regions.

**Rationale:** Data access should be scoped to operational responsibility. Cross-region access requires elevated authorization.

**Business Impact if Violated:** Agents access customer records outside their jurisdiction, creating data privacy risks and potential regulatory exposure.

---

## 7. Merge Rules

---

### BR-032 — Merge Requires Supervisor Authorization

**Rule:** A customer merge operation may only be initiated and confirmed by a user with Supervisor role or above. Agents may nominate records for merge review but cannot execute it.

**Rationale:** Merging records is a high-risk, irreversible action. It must be subject to an elevated level of human authorization.

**Business Impact if Violated:** Records are merged incorrectly without oversight, permanently corrupting customer data.

---

### BR-033 — Merge Designates One Survivor

**Rule:** Every merge operation must explicitly designate one record as the **survivor** and one as the **non-survivor**. The survivor's customer ID becomes the canonical identifier. The non-survivor's data fields may optionally be retained on the survivor at the Supervisor's discretion.

**Rationale:** The outcome of a merge must be unambiguous. A single canonical record must emerge.

**Business Impact if Violated:** Merge outcome is ambiguous; downstream systems receive conflicting identifiers.

---

### BR-034 — Merge is Irreversible

**Rule:** Once a merge operation is confirmed, it cannot be undone through the application. Reversal requires a manual data remediation process.

**Rationale:** Downstream systems have already received and acted on the merge event. Automated reversal would require complex compensating transactions across all integrated systems.

**Business Impact if Violated:** If a bad merge is silently reversed, downstream systems become inconsistent with the Customer Management system.

---

### BR-035 — Non-Survivor Retained for Audit

**Rule:** The non-surviving record from a merge must be retained in the system in a **Merged** status indefinitely. It must not be deleted. It must be linked to the surviving record.

**Rationale:** Regulators, legal teams, and auditors may need to trace the history of a customer through identity changes and record consolidations.

**Business Impact if Violated:** Historical records are lost. The organization cannot respond to legal discovery or regulatory audit requests for the non-surviving customer's history.

---

### BR-036 — Only One Active Merge Per Record

**Rule:** A customer record that is already the subject of an in-progress merge operation cannot be included in a second merge until the first is completed or cancelled.

**Rationale:** Concurrent merges on the same record create race conditions and indeterminate outcomes.

**Business Impact if Violated:** Data corruption as two concurrent merge processes produce conflicting survivor states.

---

### BR-037 — Downstream Systems Notified on Merge

**Rule:** Upon completion of a merge, all registered downstream systems must receive a merge event containing both the non-surviving and surviving customer IDs.

**Rationale:** Downstream systems must update their own references from the non-surviving ID to the surviving ID.

**Business Impact if Violated:** Downstream systems continue to reference the non-surviving ID, causing billing, case, and communication failures.

---

## 8. Security & Permission Rules

---

### BR-038 — Role-Based Access Enforcement

**Rule:** Every action in the system — create, read, update, status change, merge, delete — must be evaluated against the requesting user's assigned role before execution. Unauthorized actions must be rejected, not silently ignored.

**Rationale:** Role-based access control is the primary mechanism for enforcing data governance and accountability.

**Business Impact if Violated:** Unauthorized users can read, modify, or delete customer records, creating data privacy, integrity, and compliance failures.

---

### BR-039 — Restricted Fields Require Elevated Role

**Rule:** Fields classified as sensitive (national identifiers, compliance flags, consent records) must only be readable and editable by users with Supervisor or Administrator role. These fields must be masked or hidden for users with Viewer or Agent role.

**Rationale:** Sensitive fields carry regulatory obligations. Access must be strictly limited to personnel with a legitimate need.

**Business Impact if Violated:** Regulatory breach through unauthorized access to personally identifiable or regulated data.

---

### BR-040 — Session Timeout Enforces Re-authentication

**Rule:** An authenticated user session must expire after a configurable period of inactivity (default: 30 minutes). The user must re-authenticate before continuing any action.

**Rationale:** Unattended sessions on shared workstations create an unauthorized access vector.

**Business Impact if Violated:** A third party uses an unattended session to access or modify customer records without authorization.

---

### BR-041 — API Access Governed by Integration Contract

**Rule:** System integrations accessing the Customer Management API must authenticate using a service credential issued under a defined integration contract. Credentials must be scoped to the minimum required permissions and must expire on a defined schedule.

**Rationale:** Uncontrolled API access is a significant data exfiltration and integrity risk.

**Business Impact if Violated:** An unauthorized or compromised integration reads or writes customer data at scale, causing a data breach.

---

### BR-042 — Administrator Cannot Self-Assign Permissions

**Rule:** An Administrator may not modify their own role, permissions, or access scope. Permission changes for Administrators require a second Administrator to authorize.

**Rationale:** Self-assignment of elevated permissions bypasses the segregation of duties control.

**Business Impact if Violated:** An Administrator escalates their own access without oversight, creating an undetectable privilege escalation risk.

---

## 9. Audit & Compliance Rules

---

### BR-043 — All Changes Produce Audit Entries

**Rule:** Every create, update, status change, merge, and permission change must produce an audit log entry recording: the action type, the fields affected, the before and after values, the user or system that performed the action, and the timestamp.

**Rationale:** A complete audit trail is required for regulatory compliance, dispute resolution, and forensic investigation.

**Business Impact if Violated:** The organization cannot demonstrate compliance with data governance obligations and cannot reconstruct the history of a customer record.

---

### BR-044 — Audit Log is Immutable

**Rule:** Audit log entries cannot be edited or deleted by any user role, including Administrator. Attempts to modify audit entries must be rejected and themselves logged.

**Rationale:** An editable audit log provides no evidentiary value. Regulators require tamper-proof records.

**Business Impact if Violated:** The organization cannot rely on the audit log for legal, regulatory, or dispute purposes.

---

### BR-045 — Consent State is Versioned

**Rule:** Every change to a customer's consent flags must create a new versioned consent record rather than overwriting the existing one. The full consent history must be retained and queryable.

**Rationale:** Regulators may require the organization to demonstrate the state of customer consent at any historical point in time.

**Business Impact if Violated:** The organization cannot prove what consent was held at a given time, exposing it to regulatory penalties and legal liability.

---

### BR-046 — Audit Retention is Indefinite

**Rule:** Audit log records are not subject to automated data retention deletion policies. They must be retained for the lifetime of the system and any successor systems.

**Rationale:** Legal and regulatory obligations may require historical audit data years or decades after the events occurred.

**Business Impact if Violated:** The organization purges audit data needed for regulatory inquiry or legal discovery.

---

## 10. Data Integrity Rules

---

### BR-047 — Required Fields Cannot be Blanked

**Rule:** Once a mandatory field has been populated on a customer record, it cannot be set to null or empty by a subsequent update. Any attempt must be rejected with a validation error.

**Rationale:** Mandatory fields define the minimum viable state of a customer record. Blanking them degrades the record below the minimum standard.

**Business Impact if Violated:** Records lose mandatory data, causing failures in downstream systems that depend on those fields.

---

### BR-048 — Customer Name Cannot Contain Only Whitespace

**Rule:** First name and last name fields must contain at least one non-whitespace character. Names consisting solely of spaces, tabs, or other whitespace must be rejected.

**Rationale:** Whitespace-only names are not meaningful identifiers and indicate data entry errors.

**Business Impact if Violated:** Records with blank-appearing names pass validation and enter the system, causing search, display, and communication failures.

---

### BR-049 — Date Fields Must be Chronologically Valid

**Rule:** All date fields must be logically valid. Date of birth must be in the past. Created date must not be in the future. Where date ranges are captured, the end date must be on or after the start date.

**Rationale:** Invalid dates indicate data entry errors and can cause calculation failures in downstream systems.

**Business Impact if Violated:** Downstream systems produce incorrect age calculations, eligibility determinations, or date-based reporting.

---

### BR-050 — Referential Integrity for Linked Records

**Rule:** A customer record cannot be linked to a case, note, or external reference that does not exist in the system. Orphaned or dangling references must be rejected at the point of creation.

**Rationale:** Dangling references cause failures when systems attempt to retrieve linked records and find nothing.

**Business Impact if Violated:** Staff and systems encounter broken links, and reports include references to non-existent records.

---

## 11. Error Handling Rules

---

### BR-051 — Validation Errors Returned with Field-Level Detail

**Rule:** When a create or update operation is rejected due to validation failure, the system must return a response identifying each invalid field and a human-readable reason for the rejection. Generic or single-message errors are not acceptable.

**Rationale:** Field-level error messages allow staff and integrations to correct specific problems without guessing.

**Business Impact if Violated:** Staff cannot determine what is wrong with a submission, increasing resolution time and error rates.

---

### BR-052 — Rejected Transitions Return Business Reason

**Rule:** When a status transition is rejected, the system must return the specific business reason (e.g., "Customer has 2 open cases", "Outstanding balance of £340.00"). The response must be actionable.

**Rationale:** Staff must understand why a transition was blocked in order to resolve the blocking condition.

**Business Impact if Violated:** Staff cannot resolve the blocking condition and must escalate unnecessarily, increasing handling time.

---

### BR-053 — Concurrent Edit Conflict Must Be Detected

**Rule:** If two users attempt to save changes to the same customer record simultaneously, the system must detect the conflict and reject the second save with an explicit conflict notification. The second user must be shown the current saved state before re-attempting their edit.

**Rationale:** Last-write-wins behavior silently overwrites changes, causing data loss and integrity failures.

**Business Impact if Violated:** One user's changes overwrite another's without either user being aware, causing data loss and conflicting records.

---

## 12. Reporting Rules

---

### BR-054 — Closed and Merged Records Excluded from Live Metrics

**Rule:** Operational reports and dashboards reflecting live customer counts, status distributions, and activity metrics must exclude records with Closed or Merged status, unless the report is explicitly a historical or lifecycle report.

**Rationale:** Including closed and merged records in live metrics inflates counts and misrepresents the active customer base.

**Business Impact if Violated:** Leadership and operational teams make decisions based on inflated or inaccurate customer volume figures.

---

### BR-055 — Status Distribution Report Reflects Point-in-Time State

**Rule:** Any report showing the distribution of customers by status must be generated against a declared point-in-time snapshot, not a live query that may change during report generation.

**Rationale:** A live query run over a period of time may capture different records in different states, producing an internally inconsistent report.

**Business Impact if Violated:** Status reports are internally inconsistent and cannot be relied upon for operational or regulatory purposes.

---

### BR-056 — Duplicate Resolution Rate is a Tracked Metric

**Rule:** The system must track and make available the following duplicate-related metrics: total duplicate flags raised, flags resolved by merge, flags dismissed, and average time to resolution. These must be reportable by time period and user.

**Rationale:** Duplicate proliferation is a leading indicator of data quality degradation. Tracking resolution rate allows the organization to detect and respond to worsening duplicate rates.

**Business Impact if Violated:** The organization has no visibility into the health of its duplicate resolution process and cannot detect or respond to deteriorating data quality.
