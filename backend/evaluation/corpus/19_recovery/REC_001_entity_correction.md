---
id: REC_001
category: recovery
difficulty: hard
scenario_name: Mid-Turn Entity Correction and Context Recovery
expected_outcomes:
  initial_entity: solution_ecommerce_os
  pricing_speculation_allowed: false
  hallucination_allowed: false

turns:
  - turn: 1
    user: "Tell me about Ecommerce OS."
    expected_state:
      active_entity: solution_ecommerce_os
      active_registry: SOLUTIONS
    expected_response:
      must_include: ["E-Commerce OS"]

  - turn: 2
    user: "How scalable is it?"
    expected_state:
      active_entity: solution_ecommerce_os
    expected_response:
      must_include: ["scalable"]

  - turn: 3
    user: "Actually I meant Pharma OS."
    expected_state:
      active_entity: solution_pharma_os
      previous_entity: solution_ecommerce_os
      topic_switch_detected: true
    expected_response:
      must_include: ["Pharma OS"]
      must_not_include: ["E-Commerce OS"]

  - turn: 4
    user: "How secure is it?"
    expected_state:
      active_entity: solution_pharma_os
      inherited_context: true
    expected_response:
      must_include: ["secure", "clinical", "batch"]
---

Customer:
Tell me about Ecommerce OS.

Assistant:
🏆 **E-Commerce OS**

Customer:
How scalable is it?

Assistant:
It is built for enterprise scale.

Customer:
Actually I meant Pharma OS.

Assistant:
🏥 **Pharma & Healthcare OS**

Customer:
How secure is it?

Assistant:
Pharma OS provides secure clinical file management and batch tracking compliance.
