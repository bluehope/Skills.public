---
registration_schema_version: 1
candidate_id: null
reference_id: null
reference_litmus: null
observable_id: null
unit_id: null
consumer_id: null
condition_fingerprint: "sha256:<64-hex>"
workflow_profile: core
consumer_identity_recorded: false
same_observable_reference_checked: false
route_equal_control_status: pending
self_reference_used_as_validation: true
user_named_raw_status: pending
---

# Registration checklist for `<candidate_id>`

- Consumer/assembler identity recorded: `<consumer_identity_recorded>`
- Same-observable independent reference checked: `<same_observable_reference_checked>`
- Measurement-route EQUAL control: `<route_equal_control_status>`
- Self-reference used as validation: `<self_reference_used_as_validation>`
- User-named raw artifact status: `<user_named_raw_status>`

Allowed non-boolean values:

- `route_equal_control_status`: `completed` or `not-applicable`
- `user_named_raw_status`: `opened` or `not-applicable`
