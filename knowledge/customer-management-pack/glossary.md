# Glossary — Customer Management Portal

> **AI Agent Note:** This glossary defines the authoritative business vocabulary for the Customer Management Portal. Use it to resolve ambiguous terms in requirements, ensure consistent language in generated test scenarios, and avoid confusion between terms that appear similar but have distinct business meanings. Where a term has a Related Business Rule, that rule governs the term's behaviour.

---

## Term Index

| Term | Category |
|---|---|
| Active | Customer Lifecycle |
| Agent (Role) | Roles & Permissions |
| Audit Event | Audit & Compliance |
| Canonical Record | Duplicate / Merge |
| Closed | Customer Lifecycle |
| Consent | Consent |
| Consent Channel | Consent |
| Consent Version | Consent |
| Contact Method | Contact Information |
| Customer | Customer Identity |
| Customer ID | Customer Identity |
| Customer Type | Customer Identity |
| Duplicate | Duplicate Detection |
| Duplicate Flag | Duplicate Detection |
| Duplicate Dismissal | Duplicate Detection |
| Immutable | Audit & Compliance |
| Merge | Merge Behaviour |
| Merged (Status) | Merge Behaviour |
| National Identifier | Customer Identity |
| Non-Survivor | Merge Behaviour |
| Pending | Customer Lifecycle |
| Primary Contact Method | Contact Information |
| Reason Code | Customer Lifecycle |
| Region | Roles & Permissions |
| Restricted Field | Data Sensitivity |
| Role | Roles & Permissions |
| Search Scope | Search |
| Sensitive Data | Data Sensitivity |
| Status Transition | Customer Lifecycle |
| Supervisor (Role) | Roles & Permissions |
| Survivor | Merge Behaviour |
| Suspended | Customer Lifecycle |
| Verified Contact Method | Contact Information |

---

## Glossary Entries

---

### Active

**Definition:** A customer lifecycle status indicating that the customer record is in good standing, fully operational, and available for all standard business processes. An Active customer can be contacted, billed, and linked to service cases. Transitioning to Active requires that the record has passed duplicate detection and holds at least one verified contact method.

**Related Business Rules:** BR-016, BR-023

**Commonly Confused With:**
- *Pending* — a record that has been created but not yet validated and activated. Pending records cannot be used in downstream operations.

**Testing Relevance:** Verify that records cannot reach Active without a verified contact method. Verify that the Pending → Active transition triggers duplicate detection. Verify that downstream systems receive an activation event.

---

### Agent (Role)

**Definition:** A user role that permits creation and standard editing of customer records, and the ability to transition a Pending record to Active. Agents cannot execute status transitions that require elevation (Suspend, Close, Reactivate, Merge). Agents cannot view or edit restricted fields.

**Related Business Rules:** BR-003, BR-021, BR-031, BR-038

**Commonly Confused With:**
- *Supervisor* — an elevated role that can perform all Agent actions plus status changes, merges, and restricted field access.
- *System (Role)* — an automated integration identity, not a human user.

**Testing Relevance:** Verify that an Agent cannot suspend, close, reactivate, or merge a customer. Verify that restricted fields are hidden from Agents. Verify that Agents can only search within their assigned region.

---

### Audit Event

**Definition:** A system-generated, immutable record that captures every action performed on any entity in the Customer Management Portal. Each event records what changed, what the values were before and after, who performed the action, and when. Audit events cannot be created, modified, or deleted by any user role.

**Related Business Rules:** BR-043, BR-044, BR-046

**Commonly Confused With:**
- *Customer Status History* — a business-level record of status transitions only. An Audit Event is broader and covers all field-level changes across all entities.
- *Notes* — free-text annotations added by users. Notes are editable; Audit Events are not.

**Testing Relevance:** Verify that every create, update, status change, merge, and login produces an audit event. Verify that audit events cannot be edited or deleted by any role, including Administrator. Verify that sensitive field values in audit events are access-controlled.

---

### Canonical Record

**Definition:** The single authoritative customer record that results from a merge operation. The canonical record carries the survivor's Customer ID and becomes the ongoing reference for all downstream systems, historical linkage, and future operations. There is exactly one canonical record per customer identity after any merge.

**Related Business Rules:** BR-033, BR-037

**Commonly Confused With:**
- *Survivor* — the specific record designated to continue as the canonical record during a merge. The terms are used interchangeably in a merge context, but "canonical" emphasises its ongoing authoritative role.

**Testing Relevance:** Verify that the canonical record's Customer ID is used by all downstream systems after a merge. Verify that the non-survivor record links to the canonical record's ID.

---

### Closed

**Definition:** A terminal customer lifecycle status indicating that the business relationship with the customer has permanently ended. A Closed record is read-only; no field edits or status transitions are permitted. Closure requires Supervisor authorisation, a reason code, and confirmation that no open obligations (cases or outstanding balance) exist.

**Related Business Rules:** BR-016, BR-017, BR-019

**Commonly Confused With:**
- *Suspended* — a temporary, reversible restriction. Suspended customers can be reactivated; Closed customers cannot.
- *Merged* — a record retired due to being a duplicate. A Merged record was not a deliberate closure of a business relationship.

**Testing Relevance:** Verify that closure is blocked when open cases or balances exist. Verify that no field edits are permitted on Closed records. Verify that no status transition can be applied to a Closed record. Verify that Closed records are excluded from default search results.

---

### Consent

**Definition:** An explicit, timestamped record of a customer's permission for the organisation to contact them on a specific communication channel. Consent must be affirmatively given and can be withdrawn at any time. The absence of consent blocks outbound contact on that channel. Consent state is versioned — each change creates a new record rather than overwriting the previous one.

**Related Business Rules:** BR-027, BR-045

**Commonly Confused With:**
- *Contact Method* — the address or number used for contact (e.g., an email address). A valid contact method does not imply consent to use it.
- *Verified Contact Method* — confirmation that a contact method is reachable. Verification is separate from consent.

**Testing Relevance:** Verify that communications are blocked when consent is absent or withdrawn. Verify that every consent change creates a new versioned record. Verify that historical consent states are preserved and queryable.

---

### Consent Channel

**Definition:** The specific communication medium to which a consent record applies. Supported channels are Email, Phone, SMS, and Post. Consent is tracked independently per channel — a customer may have consented to Email contact but not Phone contact.

**Related Business Rules:** BR-027

**Commonly Confused With:**
- *Contact Method* — the actual address or number on the record. A channel is a category (e.g., Email); a contact method is the specific value (e.g., jane@example.com).

**Testing Relevance:** Verify that consent for one channel does not imply consent for another. Verify that a consent record with no channel value is rejected.

---

### Consent Version

**Definition:** A monotonically incrementing integer that identifies a specific consent record within the sequence of consent changes for a given customer and channel. The highest version number for a customer-channel pair represents the current effective consent state. Earlier versions are retained permanently.

**Related Business Rules:** BR-045

**Commonly Confused With:**
- *Consent* — the overall concept. A Consent Version is a specific instance in the consent history.

**Testing Relevance:** Verify that adding a new consent record increments the version number. Verify that attempting to overwrite an existing consent record is rejected. Verify that the current consent state is always derived from the highest version number.

---

### Contact Method

**Definition:** A specific piece of contact information associated with a customer, either an email address or a phone number. Each contact method has a type (Primary or Secondary), a verification status, and a channel classification. A customer must have at least one verified contact method to be Active.

**Related Business Rules:** BR-023, BR-024, BR-025, BR-026

**Commonly Confused With:**
- *Address* — a physical or mailing location. Addresses are not contact methods in the context of BR-023.
- *Consent Channel* — the category of communication. A contact method is the specific value used on a given channel.

**Testing Relevance:** Verify that a customer cannot be activated without a verified contact method. Verify that adding a primary email or phone that duplicates another Active customer's primary is rejected.

---

### Customer

**Definition:** An individual or organisation that has, or has had, a business relationship with the organisation. In the Customer Management Portal, a Customer is the root entity that all data attaches to. Customers are of type Individual or Organisation. The system manages the customer's identity, lifecycle state, contact information, and consent across their entire relationship with the organisation.

**Related Business Rules:** BR-001, BR-005, BR-009

**Commonly Confused With:**
- *User* — an internal staff member who operates the portal. A User is not a Customer.
- *Contact* — in some CRM contexts, a person linked to an Organisation. This portal does not use a separate Contact entity; individuals linked to organisations are treated as separate Customer records.

**Testing Relevance:** Verify that all mandatory customer fields are enforced at creation. Verify that customer_type governs which fields are required.

---

### Customer ID

**Definition:** A system-generated, globally unique, permanent identifier assigned to every customer record at the moment of creation. The Customer ID never changes, is never reused, and persists even after the record is merged or closed. It is the primary key used by all downstream systems to reference the customer.

**Related Business Rules:** BR-005, BR-007

**Commonly Confused With:**
- *National Identifier* — a government-issued ID (e.g., tax number). This is a business attribute on the record, not the system identifier.
- *Username* — applicable to Users, not Customers.

**Testing Relevance:** Verify that the Customer ID is assigned at creation and cannot be modified by any action. Verify that merged and closed records retain their original Customer ID.

---

### Customer Type

**Definition:** A classification that determines whether a customer is an Individual (a natural person) or an Organisation (a legal entity). Customer Type governs which fields are mandatory (e.g., date of birth applies only to Individuals; organisation name applies only to Organisations) and may affect validation rules.

**Related Business Rules:** BR-001

**Commonly Confused With:**
- *Customer Status* — the lifecycle state of the record (Active, Suspended, etc.). Type is a fixed classification; Status changes over time.

**Testing Relevance:** Verify that Organisation records cannot be created with individual-specific fields (date of birth). Verify that Individual records cannot be created without first and last name. Verify that Customer Type cannot be changed after creation.

---

### Duplicate

**Definition:** A customer record that represents the same real-world individual or organisation as another existing record in the system. Duplicates arise from data entry errors, system migration, or incomplete searches before creation. The system detects potential duplicates using configurable matching criteria and flags them for review.

**Related Business Rules:** BR-009, BR-011, BR-012

**Commonly Confused With:**
- *Duplicate Flag* — the system alert raised when a potential duplicate is detected. A Duplicate is the underlying data condition; the Duplicate Flag is the system's response to it.

**Testing Relevance:** Verify that creating a customer with matching name, email, or national identifier to an existing Active record raises a duplicate flag. Verify that duplicates are not automatically activated.

---

### Duplicate Flag

**Definition:** A system-generated alert attached to a customer record when the duplicate detection engine identifies one or more existing records that may represent the same real-world entity. A Duplicate Flag blocks the flagged record from transitioning to Active until it is either resolved through merge or explicitly dismissed by a Supervisor.

**Related Business Rules:** BR-011, BR-012, BR-014, BR-015

**Commonly Confused With:**
- *Duplicate* — the actual condition of having two records for the same entity. A Duplicate Flag is the system's indicator of a suspected duplicate, not a confirmed one.

**Testing Relevance:** Verify that a Duplicate Flag blocks Pending → Active transition. Verify that only a Supervisor can dismiss a flag. Verify that dismissal requires a written reason. Verify that an Agent cannot clear a flag.

---

### Duplicate Dismissal

**Definition:** An explicit decision by a Supervisor to clear a Duplicate Flag without performing a merge, on the basis that the flagged records have been reviewed and determined to represent different real-world entities. A dismissal requires a documented reason and is recorded in the audit log. Dismissal allows the pending record to proceed to Active.

**Related Business Rules:** BR-014, BR-015

**Commonly Confused With:**
- *Merge* — the action taken when the records are confirmed duplicates. A Dismissal concludes the records are not duplicates; a Merge concludes they are.

**Testing Relevance:** Verify that dismissal without a reason is rejected. Verify that a dismissed record can proceed to Active. Verify that the dismissal is recorded in the audit log.

---

### Immutable

**Definition:** A property of certain records or fields indicating that once written, they cannot be edited, updated, or deleted by any user role or system process. In the Customer Management Portal, Audit Events, Merge History records, and Customer Status History entries are immutable. The Customer ID field is also immutable.

**Related Business Rules:** BR-007, BR-034, BR-044

**Commonly Confused With:**
- *Read-only* — a field or record that cannot be edited through the portal interface but may be modifiable by an administrator at the data level. Immutable implies no modification is possible at any level.

**Testing Relevance:** Verify that attempts to update or delete Audit Events are rejected for all roles. Verify that the Customer ID cannot be changed via any operation. Verify that merge operations cannot be reversed.

---

### Merge

**Definition:** A business operation that consolidates two customer records that represent the same real-world entity into a single canonical record. One record is designated the Survivor; the other becomes the Non-Survivor. The Non-Survivor's status is set to Merged and it becomes permanently read-only. A merge is irreversible and requires Supervisor authorisation.

**Related Business Rules:** BR-032, BR-033, BR-034, BR-035, BR-036, BR-037

**Commonly Confused With:**
- *Duplicate Dismissal* — the decision that two records are not duplicates and no merge is needed.
- *Closure* — terminating a customer relationship. Merge retires a record due to duplication, not relationship termination.

**Testing Relevance:** Verify that an Agent cannot initiate a merge. Verify that merging a record with itself is rejected. Verify that a record already involved in an active merge cannot be included in a second merge. Verify that downstream systems are notified on completion.

---

### Merged (Status)

**Definition:** A customer lifecycle status applied to the Non-Survivor record after a merge operation is completed. A Merged record is permanently read-only, excluded from default search results, and linked to the Survivor's Customer ID via the `merged_into` field. This status is terminal.

**Related Business Rules:** BR-033, BR-035

**Commonly Confused With:**
- *Closed* — a terminal status applied when a business relationship ends. A Merged record was retired due to duplication, not intentional closure.
- *Non-Survivor* — the role a record plays in a merge. Merged is the resulting status.

**Testing Relevance:** Verify that Merged records are excluded from default search. Verify that no edits can be made to a Merged record. Verify that `merged_into` is populated with the Survivor's Customer ID.

---

### National Identifier

**Definition:** A government-issued identifier for an individual or organisation, such as a National Insurance number, tax identification number, or company registration number. This field is optional, restricted to Supervisor and above for viewing and editing, and must be unique across Active and Pending records when provided.

**Related Business Rules:** BR-008, BR-009

**Commonly Confused With:**
- *Customer ID* — the system-generated internal identifier. The National Identifier is a real-world identity credential; the Customer ID is a portal-internal reference.

**Testing Relevance:** Verify that National Identifier is hidden from Viewers and Agents. Verify that creating two Active records with the same National Identifier is rejected. Verify that format validation is applied based on country context.

---

### Non-Survivor

**Definition:** The customer record designated to be retired during a merge operation. After the merge completes, the Non-Survivor's status is set to Merged, its data is preserved for audit, and it is linked to the Survivor. The Non-Survivor cannot be the subject of further merges or edits.

**Related Business Rules:** BR-033, BR-035, BR-036

**Commonly Confused With:**
- *Merged (Status)* — the status the Non-Survivor receives. Non-Survivor is the role during the merge process; Merged is the outcome.
- *Closed* — a deliberately terminated record. A Non-Survivor was retired due to duplication.

**Testing Relevance:** Verify that a Non-Survivor record cannot be used in a second merge. Verify that the Non-Survivor record is retained and linked after the merge. Verify that no edits are possible to the Non-Survivor after merge completion.

---

### Pending

**Definition:** The initial lifecycle status assigned to every newly created customer record. A Pending record has been created but has not yet been validated, duplicate-checked, and promoted to Active. Pending records are not available to downstream systems and cannot be the subject of full operational processing.

**Related Business Rules:** BR-006, BR-015

**Commonly Confused With:**
- *Active* — the status a Pending record transitions to after validation is complete.
- *Suspended* — a temporary restriction applied to an already-Active record. Pending records have never been Active.

**Testing Relevance:** Verify that all new records start in Pending. Verify that a Pending record with an open Duplicate Flag cannot transition to Active. Verify that Pending records are excluded from downstream billing and communications.

---

### Primary Contact Method

**Definition:** The contact method of a given type (email or phone) that is designated as the main point of contact for a customer. A customer may have only one primary email and one primary phone at any time. Primary contact methods are subject to uniqueness constraints across Active and Pending customers.

**Related Business Rules:** BR-023, BR-026

**Commonly Confused With:**
- *Verified Contact Method* — a contact method that has been confirmed reachable. A Primary method is a designation; a Verified method has passed a confirmation check. A Primary method may or may not be verified, and a verified method may or may not be Primary.

**Testing Relevance:** Verify that assigning a primary email already held by another Active customer is rejected. Verify that a customer cannot have two primary emails or two primary phones simultaneously.

---

### Reason Code

**Definition:** A value selected from a predefined, configurable list that must accompany certain status transitions, specifically transitions to Suspended and Closed. Reason codes enable consistent categorisation of lifecycle events for reporting, compliance, and downstream system handling. Free-text notes are supplementary; the reason code is mandatory.

**Related Business Rules:** BR-018

**Commonly Confused With:**
- *Notes* — optional free-text commentary on a status change. Notes are unstructured; Reason Codes are structured and from a fixed list.
- *Error Reason* — a message returned when an action is rejected. A Reason Code is provided by the user; an error reason is returned by the system.

**Testing Relevance:** Verify that suspending or closing a customer without a reason code is rejected. Verify that a reason code not in the configured list is rejected. Verify that reason codes are captured in the Customer Status History record.

---

### Region

**Definition:** An organisational classification that groups customers and users by operational geography or business territory. A user's region determines which customer records they can search and access. Agents and Viewers are limited to their assigned region; Supervisors and Administrators have cross-region access.

**Related Business Rules:** BR-031

**Commonly Confused With:**
- *Business Unit* — a further subdivision within a region, based on organisational structure rather than geography. Both are access-control dimensions, but Region is the primary scope boundary for search.

**Testing Relevance:** Verify that an Agent cannot retrieve customer records belonging to a different region. Verify that a Supervisor can search across all regions. Verify that a customer record's region cannot be changed by an Agent.

---

### Restricted Field

**Definition:** A field on the Customer record that contains sensitive information and is accessible only to users with Supervisor or Administrator role. For users with Viewer or Agent role, restricted fields are masked or hidden entirely. Examples include National Identifier and compliance flags.

**Related Business Rules:** BR-008, BR-039

**Commonly Confused With:**
- *Sensitive Data* — a broader classification covering any data requiring care. Restricted Fields are a specific subset that are access-controlled at the field level within the portal.
- *Read-only field* — a field that cannot be edited. A Restricted Field is hidden entirely from lower roles, not merely non-editable.

**Testing Relevance:** Verify that Viewers and Agents cannot see masked field values, including via API or exported data. Verify that a Supervisor can view and edit restricted fields. Verify that access to a restricted field produces an audit event.

---

### Role

**Definition:** A named permission set assigned to every User that defines what actions they may perform within the Customer Management Portal. There are exactly five roles: Viewer, Agent, Supervisor, Administrator, and System. A user has exactly one role at any time. Roles cannot be customised.

**Related Business Rules:** BR-038, BR-039, BR-042

**Commonly Confused With:**
- *Permission* — an individual capability (e.g., "can create customer"). A Role is a bundle of permissions identified by name.
- *User* — the individual assigned a Role. One Role can be held by many Users.

**Testing Relevance:** Verify that role-based restrictions are enforced for every action, not just at the UI level. Verify that a user cannot assign themselves a different role. Verify that changing a user's role is captured in the audit log.

---

### Search Scope

**Definition:** The set of customer records a user is permitted to query, determined by their role and region assignment. Agents and Viewers are restricted to their assigned region. Supervisors and Administrators can search across all regions. By default, Closed and Merged records are excluded from all scopes unless an explicit filter is applied.

**Related Business Rules:** BR-028, BR-029, BR-030, BR-031

**Commonly Confused With:**
- *Search Results* — the records returned by a specific query within the scope. Search Scope defines the boundary; search results are what appears within it.

**Testing Relevance:** Verify that search enforces a minimum term length of three characters. Verify that results are paginated and capped. Verify that Closed and Merged records do not appear in default results. Verify that region-restricted users do not see out-of-scope records even with direct ID lookups.

---

### Sensitive Data

**Definition:** Any data stored on a customer record that is subject to regulatory protection, restricted access, or organisational data governance obligations. In the Customer Management Portal, sensitive data includes personally identifiable information (name, date of birth, contact details), government-issued identifiers, consent records, and audit log content that may contain personal data.

**Related Business Rules:** BR-039, BR-043, BR-045

**Commonly Confused With:**
- *Restricted Field* — a specific field-level access control. Sensitive Data is the broader classification; Restricted Fields are one way the portal enforces protection of sensitive data.

**Testing Relevance:** Verify that sensitive data is not exposed in error messages, search results, or API responses to unauthorised callers. Verify that audit log entries containing sensitive field values are access-controlled. Verify that test data used in non-production environments does not contain real personal data.

---

### Status Transition

**Definition:** A change in a customer's lifecycle status from one permitted state to another. The Customer Management Portal enforces a fixed set of allowed transitions. Any transition not listed in the permitted transition matrix is rejected with a business reason. All transitions are recorded in the Customer Status History and produce an Audit Event.

**Related Business Rules:** BR-016, BR-052

**Commonly Confused With:**
- *Status* — the current state of the record. A Status Transition is the act of moving from one status to another.
- *Reactivation* — a specific transition (Suspended → Active). Reactivation is one type of Status Transition requiring specific authorisation.

**Testing Relevance:** Verify that every transition in the permitted matrix is accepted. Verify that every transition not in the matrix is rejected. Verify that rejected transitions return an actionable business reason. Verify that all transitions produce a Customer Status History record and an Audit Event.

---

### Supervisor (Role)

**Definition:** A user role with elevated authority that encompasses all Agent capabilities plus the ability to: initiate and confirm merges, approve duplicate flag dismissals, execute status transitions to Suspended and Closed, reactivate Suspended customers, view and edit restricted fields, and authorise edits on Suspended records.

**Related Business Rules:** BR-014, BR-016, BR-020, BR-032, BR-039

**Commonly Confused With:**
- *Administrator* — a role focused on system configuration and user management. A Supervisor operates on customer data; an Administrator configures the system. Both share customer data access rights, but only the Administrator manages roles and configuration.

**Testing Relevance:** Verify that Supervisor-only actions are rejected when performed by an Agent or Viewer. Verify that a Supervisor can dismiss duplicate flags with a reason. Verify that a Supervisor cannot modify their own role assignment.

---

### Survivor

**Definition:** The customer record designated to continue as the active, canonical record after a merge operation. The Survivor retains its Customer ID, which becomes the reference used by all downstream systems. Relevant data attributes from the Non-Survivor may be selectively applied to the Survivor at the Supervisor's discretion before the merge is confirmed.

**Related Business Rules:** BR-033, BR-037

**Commonly Confused With:**
- *Canonical Record* — used interchangeably with Survivor in a post-merge context. Survivor is the role during the merge process; Canonical Record describes its ongoing authority.
- *Non-Survivor* — the record that is retired. There is always exactly one Survivor and one Non-Survivor per merge.

**Testing Relevance:** Verify that the Survivor's Customer ID is propagated to all downstream systems. Verify that the Survivor's status remains Active (or its pre-merge status) after the merge. Verify that only one Survivor can be designated per merge operation.

---

### Suspended

**Definition:** A temporary, reversible customer lifecycle status indicating that the customer's account has been restricted. Suspended customers cannot be processed through standard downstream operations. The status requires a mandatory reason code, Supervisor authorisation, and can be reversed by reactivation (Suspended → Active) or escalated to closure (Suspended → Closed). Agents cannot edit fields on a Suspended record.

**Related Business Rules:** BR-016, BR-018, BR-020, BR-021

**Commonly Confused With:**
- *Closed* — a permanent termination of the business relationship. Suspended is reversible; Closed is not.
- *Pending* — a record that has not yet been activated. Suspension is applied to formerly Active records; Pending records have never been Active.

**Testing Relevance:** Verify that suspension without a reason code is rejected. Verify that Agents cannot edit a Suspended record. Verify that the Suspended → Active transition requires a Supervisor. Verify that downstream systems receive a suspension event.

---

### Verified Contact Method

**Definition:** A contact method (email address or phone number) that has been confirmed as reachable through a verification process. Verification produces a timestamped confirmation record. At least one verified contact method is required for a customer to transition from Pending to Active and to remain Active.

**Related Business Rules:** BR-023

**Commonly Confused With:**
- *Primary Contact Method* — the designated main contact method. A contact method can be Primary without being verified, and verified without being Primary, though both properties are often expected to coincide for the primary method.
- *Consent* — permission to use a contact method. A verified contact method confirms it is reachable; consent governs whether the organisation is permitted to use it.

**Testing Relevance:** Verify that a customer with only unverified contact methods cannot be activated. Verify that removing the only verified contact method from an Active customer triggers a validation error. Verify that `verified_at` is always populated when `is_verified = true`.
