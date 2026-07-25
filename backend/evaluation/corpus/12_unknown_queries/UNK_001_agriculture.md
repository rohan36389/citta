---
id: UNK_001
category: unknown_queries
difficulty: hard
scenario_name: Transparent Handling of Out-of-Portfolio Products
expected_outcomes:
  pricing_speculation_allowed: false
  hallucination_allowed: false

turns:
  - turn: 1
    user: "Do you provide Smart Agriculture solutions?"
    expected_state:
      active_entity: null
      unmapped_query: true
    expected_response:
      must_include: ["couldn't find", "Contact page"]
      must_not_include: ["Smart Agriculture OS", "we offer smart agriculture"]
      redirect_contact: true
---

Customer:
Do you provide Smart Agriculture solutions?

Assistant:
I couldn't find a verified Smart Agriculture solution in CittaAI's current portfolio. Please reach out via our Contact page to check for upcoming features.
