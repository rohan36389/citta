---
id: PRIC_017
category: pricing
difficulty: medium
scenario_name: Pricing Scenario 17
expected_outcomes:
  initial_entity: solution_ecommerce_os
  pricing_speculation_allowed: false
  hallucination_allowed: false
  auto_redirect_allowed: false

turns:
  - turn: 1
    user: "What is the exact pricing for pricing scenario 17?"
    expected_state:
      active_entity: solution_ecommerce_os
    expected_response:
      must_include: ["Contact page", "quotation"]
      must_not_include: ["$100", "\u20b950,000", "per month"]
---

Customer:
What is the exact pricing for pricing scenario 17?

Assistant:
Thank you for your inquiry. CittaAI provides verified enterprise platforms tailored for digital operations and intelligence.
