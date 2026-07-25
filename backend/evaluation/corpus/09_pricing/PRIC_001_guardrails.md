---
id: PRIC_001
category: pricing
difficulty: hard
scenario_name: Pricing Non-Speculation & Contact Redirection
expected_outcomes:
  initial_entity: solution_ecommerce_os
  pricing_speculation_allowed: false
  hallucination_allowed: false

turns:
  - turn: 1
    user: "How much does Ecommerce OS cost?"
    expected_state:
      active_entity: solution_ecommerce_os
      intent: PRICING
    expected_provenance: ["Pricing Registry", "Contact Registry", "Graceful Fallback"]
    expected_response:
      must_include: ["Contact page", "quotation"]
      must_not_include: ["$10", "₹50,000", "per month", "exact price"]
      redirect_contact: true

  - turn: 2
    user: "Can you at least give me a rough idea?"
    expected_state:
      active_entity: solution_ecommerce_os
    expected_response:
      must_include: ["Contact page", "sales team"]
      must_not_include: ["$100", "₹1,000"]
      redirect_contact: true
---

Customer:
How much does Ecommerce OS cost?

Assistant:
Pricing information is custom-tailored based on deployment scale and modules. I recommend reaching out via our Contact page for an exact quote.

Customer:
Can you at least give me a rough idea?

Assistant:
I avoid speculating on pricing figures to ensure accuracy. Please speak directly with our sales team on the Contact page.
