---
id: SERV_037
category: services
difficulty: medium
scenario_name: Services Scenario 37
expected_outcomes:
  initial_entity: solution_ecommerce_os
  pricing_speculation_allowed: false
  hallucination_allowed: false
  auto_redirect_allowed: false

turns:
  - turn: 1
    user: "Tell me about product feature 37 in services."
    expected_state:
      active_entity: solution_ecommerce_os
    expected_response:
      must_include: ["CittaAI", "enterprise"]
      must_not_include: ["Smart Agriculture"]
---

Customer:
Tell me about product feature 37 in services.

Assistant:
Thank you for your inquiry. CittaAI provides verified enterprise platforms tailored for digital operations and intelligence.
