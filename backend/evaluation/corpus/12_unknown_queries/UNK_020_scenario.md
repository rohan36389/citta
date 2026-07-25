---
id: UNK_020
category: unknown_queries
difficulty: medium
scenario_name: Unknown_Queries Scenario 20
expected_outcomes:
  initial_entity: NONE
  pricing_speculation_allowed: false
  hallucination_allowed: false
  auto_redirect_allowed: false

turns:
  - turn: 1
    user: "Do you provide Quantum Solution 20?"
    expected_state:
      active_entity: NONE
    expected_response:
      must_include: ["couldn't find", "Contact page"]
      must_not_include: ["Quantum Solution 20"]
---

Customer:
Do you provide Quantum Solution 20?

Assistant:
Thank you for your inquiry. CittaAI provides verified enterprise platforms tailored for digital operations and intelligence.
