import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from agent_contracts import AgentOutput, AgentID

logger = logging.getLogger(__name__)

class ConsensusResult(BaseModel):
    summary_markdown: str
    consensus_score: float = 0.98
    participating_agents: List[str] = Field(default_factory=list)
    total_findings: int = 0
    total_recommendations: int = 0
    unified_recommendations: List[str] = Field(default_factory=list)

class ConsensusBuilder:
    def __init__(self):
        pass

    def build_consensus(self, agent_outputs: List[AgentOutput], task: str) -> ConsensusResult:
        participating = [out.agent_id for out in agent_outputs if out.status in ["SUCCESS", "FALLBACK"]]
        all_recs = []
        all_findings = []

        lines = [f"### Enterprise Multi-Agent Consensus Summary\n**Task**: {task}\n"]

        # 1. Group Findings by Agent
        lines.append("#### Specialized Agent Findings")
        for out in agent_outputs:
            if out.status not in ["SUCCESS", "FALLBACK"]:
                continue

            status_note = f" (Fallback)" if out.status == "FALLBACK" else ""
            lines.append(f"\n- **{out.agent_id}**{status_note} (Confidence: `{out.confidence}`):")
            for f in out.findings:
                lines.append(f"  • {f}")
                all_findings.append(f)

            for r in out.recommendations:
                if r not in all_recs:
                    all_recs.append(r)

        # 2. Unified Strategic Recommendations
        lines.append("\n#### Unified Strategic Recommendations")
        for idx, rec in enumerate(all_recs, 1):
            lines.append(f"{idx}. {rec}")

        # 3. Consensus Confidence Score Calculation
        valid_outputs = [out for out in agent_outputs if out.status in ["SUCCESS", "FALLBACK"]]
        avg_conf = sum(out.confidence for out in valid_outputs) / max(len(valid_outputs), 1)
        consensus_score = round(avg_conf, 2)

        return ConsensusResult(
            summary_markdown="\n".join(lines),
            consensus_score=consensus_score,
            participating_agents=participating,
            total_findings=len(all_findings),
            total_recommendations=len(all_recs),
            unified_recommendations=all_recs
        )

_consensus_builder_instance = None

def get_consensus_builder() -> ConsensusBuilder:
    global _consensus_builder_instance
    if _consensus_builder_instance is None:
        _consensus_builder_instance = ConsensusBuilder()
    return _consensus_builder_instance
