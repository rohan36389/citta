---
id: PROD_001
category: products
difficulty: medium
scenario_name: E-Commerce OS Coreference & Capabilities
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
      minimum_confidence: 0.85
    expected_provenance: ["Registry Object Match: solution_ecommerce_os", "canonical"]
    expected_response:
      must_include: ["E-Commerce OS", "retail"]
      must_not_include: ["Smart Cities", "WhatsApp Marketing"]
      should_end_with_followup: true

  - turn: 2
    user: "Is it scalable?"
    expected_state:
      active_entity: solution_ecommerce_os
      inherited_context: true
    expected_response:
      must_include: ["scalable", "volume", "performance"]

  - turn: 3
    user: "Does it integrate with SAP?"
    expected_state:
      active_entity: solution_ecommerce_os
    expected_response:
      must_include: ["SAP", "integration", "inventory"]
---

Customer:
Tell me about Ecommerce OS.

Assistant:
🏆 **E-Commerce OS**

Run everything—from storefront to supply chain to support.

Customer:
Is it scalable?

Assistant:
Yes, E-Commerce OS is built for high-volume enterprise operations.

Customer:
Does it integrate with SAP?

Assistant:
Yes, E-Commerce OS integrates with enterprise ERP systems including SAP for real-time inventory and billing sync.
