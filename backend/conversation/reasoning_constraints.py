from dataclasses import dataclass

@dataclass
class ReasoningConstraints:
    """Reasoning constraints adapting LLM output parameters."""
    max_words: int = 250
    reading_level: str = "Enterprise Pre-Sales / Executive"
    response_depth: str = "Balanced"
    bullet_limit: int = 4
    table_allowed: bool = True
    workflow_allowed: bool = True
    comparison_allowed: bool = True
    analogy_allowed: bool = False
    click_only_redirection: bool = True  # Never force automatic browser navigation
