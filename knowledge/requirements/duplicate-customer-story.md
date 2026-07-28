# Duplicate Customer Story

## User Story

**As a** Customer Service Agent,
**I want** the system to automatically detect and flag potential duplicate customer records when I create a new customer,
**So that** the organisation maintains a single, accurate customer record and avoids the data integrity, billing, and compliance failures caused by duplicate accounts.

## Background

Customer records are the system of record for all downstream operations including billing, communications, and case management. A duplicate customer record causes split histories, misrouted communications, and regulatory reporting errors. The system must prevent duplicate records from reaching Active status without authorised review.

## Acceptance Criteria

**AC-1:** Given I am a logged-in Agent, when I submit a new customer creation request, then the system must automatically run duplicate detection against all Active and Pending customer records before the record is saved.

**AC-2:** Given duplicate detection identifies one or more potential matches, when the new customer record is created, then the system must raise a Duplicate Flag on the new record and retain its status as Pending.

**AC-3:** Given a Duplicate Flag exists on a Pending record, when a Supervisor opens the flagged record, then the system must display the list of matching records alongside the flagged record to support comparison and review.

**AC-4:** Given a Duplicate Flag is open on a Pending record, when a Supervisor dismisses the flag and provides a written reason, then the flag is cleared and the record becomes eligible to transition to Active, subject to all other activation requirements being met.

**AC-5:** Given a Duplicate Flag is open on a Pending record, when a Supervisor initiates a merge and designates the survivor record, then the system must complete the merge, set the non-survivor record to Merged status, link the non-survivor to the survivor, and notify all downstream systems.

**AC-6:** Given a Duplicate Flag is open on a Pending record, when an Agent attempts to dismiss the flag or initiate a merge, then the system must reject the action and return a clear error message indicating that Supervisor authorisation is required.

**AC-7:** The duplicate detection algorithm must evaluate the following fields when comparing a new record against existing records: first name, last name, primary email address, primary phone number, and national identifier (when provided on both records being compared).

**AC-8:** Given a Pending record has an open Duplicate Flag, when an Agent attempts to transition the record to Active, then the system must reject the transition and return a message stating that an open Duplicate Flag must be resolved before activation.

## Notes

- Duplicate detection is advisory at creation: if no matching records are found, the system must not block creation.
- Duplicate detection sensitivity (matching thresholds and field weights) is configurable per environment.
- Secondary email addresses and secondary phone numbers must not be used as matching inputs for duplicate detection.
- The merge operation is irreversible. Supervisors must review both records before confirming.
- This story covers the creation-triggered duplicate detection path. Update-triggered detection (BR-012) is out of scope for this story.
