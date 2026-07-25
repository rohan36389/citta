import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

POLICIES_DIR = Path(__file__).resolve().parent / "policies"
DEFAULT_POLICY_PATH = POLICIES_DIR / "behavior_policy_v1.yaml"


class BehaviorPolicy:
    """
    Centralized Enterprise Behavior Policy loader and configuration accessor.
    Reads versioned YAML policies to define assistant behavior across all pipeline components.
    """
    def __init__(self, policy_path: Optional[Path] = None):
        self.policy_path = policy_path or DEFAULT_POLICY_PATH
        self.config: Dict[str, Any] = {}
        self.load_policy()

    def load_policy(self):
        if self.policy_path.exists():
            try:
                with open(self.policy_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"Loaded BehaviorPolicy '{self.config.get('policy_name')}' v{self.config.get('version')}")
            except Exception as e:
                logger.error(f"Error loading behavior policy from {self.policy_path}: {e}")
                self._load_fallback_policy()
        else:
            self._load_fallback_policy()

    def _load_fallback_policy(self):
        self.config = {
            "version": "1.0-fallback",
            "behavior_rules": {
                "progressive_disclosure": True,
                "consultative_mode": True,
                "pricing_guardrail": "STRICT_NO_SPECULATION",
                "ambiguity_first": True,
                "followup_required": True,
                "max_information_density": "MEDIUM_250_WORDS",
                "enterprise_persona": True,
                "auto_redirect": False
            },
            "target_word_count": {"min_words": 100, "max_words": 250, "ideal_words": 180}
        }

    @property
    def progressive_disclosure(self) -> bool:
        return self.config.get("behavior_rules", {}).get("progressive_disclosure", True)

    @property
    def consultative_mode(self) -> bool:
        return self.config.get("behavior_rules", {}).get("consultative_mode", True)

    @property
    def pricing_guardrail(self) -> str:
        return self.config.get("behavior_rules", {}).get("pricing_guardrail", "STRICT_NO_SPECULATION")

    @property
    def ambiguity_first(self) -> bool:
        return self.config.get("behavior_rules", {}).get("ambiguity_first", True)

    @property
    def followup_required(self) -> bool:
        return self.config.get("behavior_rules", {}).get("followup_required", True)

    @property
    def auto_redirect(self) -> bool:
        return self.config.get("behavior_rules", {}).get("auto_redirect", False)

    @property
    def max_words(self) -> int:
        return self.config.get("target_word_count", {}).get("max_words", 250)


_global_behavior_policy: Optional[BehaviorPolicy] = None

def get_behavior_policy() -> BehaviorPolicy:
    global _global_behavior_policy
    if _global_behavior_policy is None:
        _global_behavior_policy = BehaviorPolicy()
    return _global_behavior_policy
