---
id: CORE_001
category: coreference
difficulty: medium
scenario_name: Pronoun Resolution Across Turn Sequence
expected_outcomes:
  initial_entity: solution_smart_cities_os
  pricing_speculation_allowed: false
  hallucination_allowed: false

turns:
  - turn: 1
    user: "Do they offer smart cities services?"
    expected_state:
      active_entity: solution_smart_cities_os
      active_registry: SOLUTIONS
    expected_response:
      must_include: ["Smart Cities OS", "urban"]

  - turn: 2
    user: "How does it work?"
    expected_state:
      active_entity: solution_smart_cities_os
      inherited_context: true
    expected_response:
      must_include: ["IoT", "mobility", "utilities"]
      must_not_include: ["WhatsApp", "Pharma OS"]

  - turn: 3
    user: "Who is it designed for?"
    expected_state:
      active_entity: solution_smart_cities_os
      inherited_context: true
    expected_response:
      must_include: ["city", "planning", "urban", "mobility"]
---

Customer:
Do they offer smart cities services?

Assistant:
⚙️ **Smart Cities OS**

Customer:
How does it work?

Assistant:
Smart Cities OS aggregates IoT sensor data and mobility feeds to optimize municipal utility management.

Customer:
Who is it designed for?

Assistant:
It is designed for city planners, municipal leaders, and urban infrastructure teams.
