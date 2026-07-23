import logging
from typing import Dict, Any, List, Optional, Tuple
from backend.conversation.models import (
    BusinessIntent,
    RolePersona,
    ResponseStrategyType,
    ResponseSectionBlueprint,
    ResponsePlan,
    IntentAnalysis,
    PersonaProfile,
    ConversationContext
)

logger = logging.getLogger(__name__)

# Strategy Blueprints Definition
STRATEGY_TEMPLATES: Dict[ResponseStrategyType, Dict[str, Any]] = {
    ResponseStrategyType.EXECUTIVE_SUMMARY: {
        "tone": "Strategic, Direct & Outcome-Oriented",
        "depth": "High-Level Executive",
        "length": "Concise (<150w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Executive Overview",
                purpose="Summarize value proposition and business impact",
                key_points=["Core business value proposition", "Key efficiency drivers"]
            ),
            ResponseSectionBlueprint(
                title="Commercial ROI & Impact",
                purpose="Highlight ROI metrics and scalability benefits",
                key_points=["Estimated ROI timeframe", "Cost reduction highlights"]
            ),
            ResponseSectionBlueprint(
                title="Strategic Next Steps",
                purpose="Outline recommended evaluation pathway",
                key_points=["Executive alignment call", "Custom ROI modeling"]
            )
        ],
        "follow_up": "Would you like a customized ROI breakdown for your team's current volume?",
        "cta": "Schedule a 15-minute executive brief with our solutions director."
    },
    ResponseStrategyType.TECHNICAL_DEEP_DIVE: {
        "tone": "Precise, Technical & Authoritative",
        "depth": "Deep Technical Specs",
        "length": "Comprehensive (300-500w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Architecture & System Boundaries",
                purpose="Detail underlying tech stack and system boundaries",
                key_points=["Microservices architecture", "Database & storage engine"]
            ),
            ResponseSectionBlueprint(
                title="API & Integration Mechanisms",
                purpose="Explain authentication, endpoints, and webhooks",
                key_points=["OAuth2 & JWT authentication", "REST & GraphQL endpoints", "Event-driven webhooks"]
            ),
            ResponseSectionBlueprint(
                title="Security, Compliance & Isolation",
                purpose="Verify encryption standards and tenant isolation",
                key_points=["AES-256 at rest", "TLS 1.3 in transit", "SOC2 / ISO27001 compliance"]
            )
        ],
        "follow_up": "Shall we provide access to our developer sandbox and OpenAPI spec?",
        "cta": "Request API sandbox keys and technical documentation access."
    },
    ResponseStrategyType.COMPARISON: {
        "tone": "Objective, Analytical & Comparative",
        "depth": "Functional & Technical Matrix",
        "length": "Balanced (150-300w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Comparative Overview",
                purpose="Frame architectural and functional differences",
                key_points=["High-level positioning comparison", "Target enterprise use cases"]
            ),
            ResponseSectionBlueprint(
                title="Feature & Capability Matrix",
                purpose="Compare key technical and operational capabilities",
                key_points=["Scalability benchmarks", "Integration ecosystem", "Deployment flexibility"]
            ),
            ResponseSectionBlueprint(
                title="Decision Framework",
                purpose="Guide solution selection based on organization priorities",
                key_points=["When to choose Option A", "When to choose Option B"]
            )
        ],
        "follow_up": "Which specific technical requirement is most critical for your evaluation?",
        "cta": "Download our comprehensive competitive evaluation report."
    },
    ResponseStrategyType.SALES_CONVERSATION: {
        "tone": "Persuasive, Value-Driven & Commercial",
        "depth": "Commercial Overview",
        "length": "Balanced (150-300w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Commercial Offering Overview",
                purpose="Present platform capabilities in relation to investment",
                key_points=["Tiered package capabilities", "Enterprise licensing model"]
            ),
            ResponseSectionBlueprint(
                title="Value Proposition & Business Case",
                purpose="Reinforce payback period and efficiency gains",
                key_points=["Fast time-to-value", "Dedicated Customer Success Manager"]
            ),
            ResponseSectionBlueprint(
                title="Commercial Proposal Pathway",
                purpose="Outline steps for tailored proposal and trial",
                key_points=["Custom quote estimation", "Proof-of-Concept scope"]
            )
        ],
        "follow_up": "Would you like our team to prepare a tailored commercial proposal?",
        "cta": "Book a custom pricing consultation with our commercial team."
    },
    ResponseStrategyType.CONSULTATIVE_DISCUSSION: {
        "tone": "Empathetic, Insightful & Advisory",
        "depth": "Consultative Alignment",
        "length": "Balanced (150-300w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Current Challenge Analysis",
                purpose="Acknowledge operational context and pain points",
                key_points=["Identified friction points", "Industry benchmark context"]
            ),
            ResponseSectionBlueprint(
                title="Recommended Strategy & Alignment",
                purpose="Map CittaAI solutions to customer objectives",
                key_points=["Phased rollout approach", "Key performance indicators"]
            ),
            ResponseSectionBlueprint(
                title="Collaborative Next Steps",
                purpose="Propose joint discovery and requirements scoping",
                key_points=["Discovery workshop", "Stakeholder interview"]
            )
        ],
        "follow_up": "What is the primary operational metric your team aims to improve this quarter?",
        "cta": "Schedule a discovery workshop with our solution architects."
    },
    ResponseStrategyType.EDUCATIONAL: {
        "tone": "Informative, Clear & Educational",
        "depth": "Introductory / Educational",
        "length": "Balanced (150-300w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Core Concept Explanation",
                purpose="Define core concepts and domain context",
                key_points=["Definition of terms", "Foundational principles"]
            ),
            ResponseSectionBlueprint(
                title="How It Operates",
                purpose="Explain practical mechanics and workflows",
                key_points=["Key components", "Data movement flow"]
            ),
            ResponseSectionBlueprint(
                title="Real-World Relevance",
                purpose="Illustrate practical applications in enterprise environments",
                key_points=["Common enterprise use cases", "Industry adoption trends"]
            )
        ],
        "follow_up": "Would you like to see a live demonstration of these concepts in action?",
        "cta": "Explore our knowledge base and architecture whitepapers."
    },
    ResponseStrategyType.RECOMMENDATION: {
        "tone": "Authoritative, Prescriptive & Tailored",
        "depth": "Prescriptive Guidance",
        "length": "Balanced (150-300w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Recommended Solution",
                purpose="Explicitly name and prescribe the optimal product/solution",
                key_points=["Primary solution recommendation", "Core fit rationale"]
            ),
            ResponseSectionBlueprint(
                title="Why This Fits Your Goals",
                purpose="Connect recommendation directly to identified customer goals",
                key_points=["Goal-to-feature mapping", "Expected outcome metrics"]
            ),
            ResponseSectionBlueprint(
                title="Implementation Roadmap",
                purpose="Outline recommended adoption sequence",
                key_points=["Phase 1 pilot setup", "Phase 2 enterprise expansion"]
            )
        ],
        "follow_up": "Does this recommendation align with your technical team's priorities?",
        "cta": "Initiate a 14-day guided proof-of-concept for this recommendation."
    },
    ResponseStrategyType.REQUIREMENTS_DISCOVERY: {
        "tone": "Inquisitive, Diagnostic & Structured",
        "depth": "Diagnostic Scoping",
        "length": "Concise (<150w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Preliminary Scoping Overview",
                purpose="Summarize understood parameters so far",
                key_points=["Captured requirements", "Environment constraints"]
            ),
            ResponseSectionBlueprint(
                title="Key Discovery Questions",
                purpose="Ask targeted diagnostic questions to complete scoping",
                key_points=["Expected monthly query volume", "Existing CRM / ERP integrations", "Target launch timeline"]
            )
        ],
        "follow_up": "Sharing these details will allow us to design an exact technical architecture.",
        "cta": "Complete our 2-minute technical requirements assessment."
    },
    ResponseStrategyType.FAQ: {
        "tone": "Direct, Concise & Informative",
        "depth": "FAQ / Direct Answer",
        "length": "Concise (<150w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Direct Answer",
                purpose="Provide immediate, unambiguous answer to inquiry",
                key_points=["Core answer statement", "Key qualification condition"]
            ),
            ResponseSectionBlueprint(
                title="Additional Context",
                purpose="Offer brief supporting detail or common edge cases",
                key_points=["Standard SLA guarantee", "Support channel availability"]
            )
        ],
        "follow_up": "Is there another aspect of this topic you would like to clarify?",
        "cta": "Browse our complete Product FAQ and documentation portal."
    },
    ResponseStrategyType.STEP_BY_STEP: {
        "tone": "Instructional, Sequential & Clear",
        "depth": "Step-by-Step Procedure",
        "length": "Balanced (150-300w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Prerequisites",
                purpose="List initial requirements and setup prerequisites",
                key_points=["API keys & credentials", "Environment setup"]
            ),
            ResponseSectionBlueprint(
                title="Sequential Steps",
                purpose="Detail ordered step-by-step procedure",
                key_points=["Step 1: Configuration", "Step 2: Integration", "Step 3: Verification"]
            ),
            ResponseSectionBlueprint(
                title="Validation & Success Criteria",
                purpose="Explain how to verify correct completion",
                key_points=["Expected response status", "Verification logs"]
            )
        ],
        "follow_up": "Need assistance walking through these integration steps live?",
        "cta": "Access the interactive step-by-step developer tutorial."
    },
    ResponseStrategyType.IMPLEMENTATION_GUIDE: {
        "tone": "Technical, Practical & Methodical",
        "depth": "Implementation Specs",
        "length": "Comprehensive (300-500w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Deployment Architecture",
                purpose="Detail cloud/on-prem deployment topologies",
                key_points=["Containerization & Helm charts", "CI/CD deployment pipeline"]
            ),
            ResponseSectionBlueprint(
                title="Integration Milestones",
                purpose="Define core implementation phases and timelines",
                key_points=["Week 1: Staging setup", "Week 2: Data ingestion", "Week 3: Production launch"]
            ),
            ResponseSectionBlueprint(
                title="Governance & Operations",
                purpose="Outline monitoring, logging, and operational runbooks",
                key_points=["Prometheus metrics", "Health checks", "Backup policies"]
            )
        ],
        "follow_up": "Would your engineering team like to schedule an implementation sync?",
        "cta": "Download the complete Enterprise Implementation Playbook."
    },
    ResponseStrategyType.TROUBLESHOOTING: {
        "tone": "Diagnostic, Empathetic & Solution-Focused",
        "depth": "Troubleshooting & Support",
        "length": "Balanced (150-300w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Symptom & Root Cause Analysis",
                purpose="Identify common error causes and diagnostic checks",
                key_points=["Common error codes", "Diagnostic log inspection"]
            ),
            ResponseSectionBlueprint(
                title="Remediation Steps",
                purpose="Provide clear steps to resolve the issue",
                key_points=["Fix step 1", "Fix step 2", "Validation check"]
            ),
            ResponseSectionBlueprint(
                title="Support Escalation",
                purpose="Detail escalation pathway if issue persists",
                key_points=["Tier 2 support contact", "Dedicated SLA response"]
            )
        ],
        "follow_up": "Did these steps resolve the issue, or would you like to escalate to support?",
        "cta": "Submit a priority support ticket with our engineering team."
    },
    ResponseStrategyType.CASE_STUDY: {
        "tone": "Evidence-Based, Inspiring & Proof-Oriented",
        "depth": "Case Study & Benchmarks",
        "length": "Balanced (150-300w)",
        "sections": [
            ResponseSectionBlueprint(
                title="Client Background & Challenge",
                purpose="Describe industry client profile and initial challenge",
                key_points=["Enterprise client background", "Operational bottleneck"]
            ),
            ResponseSectionBlueprint(
                title="CittaAI Solution Deployed",
                purpose="Detail specific modules and configuration deployed",
                key_points=["Deployed solution modules", "Timeline to deployment"]
            ),
            ResponseSectionBlueprint(
                title="Quantified Results & Business Impact",
                purpose="Highlight verified metric improvements and ROI",
                key_points=["Percentage efficiency gain", "Cost savings achieved", "User adoption rate"]
            )
        ],
        "follow_up": "Would you like to read the full case study for this industry?",
        "cta": "Download the full enterprise case study PDF."
    }
}


class ResponsePlanningEngine:
    """
    Enterprise Response Planning Engine.
    Evaluates multi-dimensional signals (intent, persona, stage, entity, customer goals)
    and formulates a structured ResponsePlan without rendering raw text.
    """
    def select_strategy_type(
        self,
        intent_str: str,
        persona_role: RolePersona,
        stage: str,
        entity: Optional[Any],
        goals: List[str]
    ) -> Tuple[ResponseStrategyType, str]:
        """
        Decision Matrix mapping signals to one of the 13 ResponseStrategyTypes.
        Returns selected type and detailed selection reasoning string.
        """
        p_intent = intent_str.lower()
        
        # 1. Technical / Developer Intent + Technical Persona -> Technical Deep Dive or Implementation Guide
        if p_intent in ["integration", "architecture"] or persona_role in [RolePersona.DEVELOPER, RolePersona.TECHNICAL_ARCHITECT]:
            if "setup" in p_intent or "implementation" in p_intent or "how to" in p_intent:
                return (
                    ResponseStrategyType.IMPLEMENTATION_GUIDE,
                    f"Selected 'Implementation Guide' due to technical persona '{persona_role.value}' and implementation intent '{intent_str}'."
                )
            elif p_intent == "workflow":
                return (
                    ResponseStrategyType.STEP_BY_STEP,
                    f"Selected 'Step-by-Step' due to workflow intent '{intent_str}' for technical user."
                )
            elif p_intent == "comparison":
                return (
                    ResponseStrategyType.COMPARISON,
                    f"Selected 'Comparison' due to comparison intent '{intent_str}'."
                )
            else:
                return (
                    ResponseStrategyType.TECHNICAL_DEEP_DIVE,
                    f"Selected 'Technical Deep Dive' due to technical intent '{intent_str}' and technical persona '{persona_role.value}'."
                )

        # 2. Executive / Pricing Intent + Executive Persona -> Executive Summary or Sales Conversation
        if persona_role in [RolePersona.EXECUTIVE_DECISION_MAKER, RolePersona.INVESTOR]:
            if p_intent == "pricing":
                return (
                    ResponseStrategyType.EXECUTIVE_SUMMARY,
                    f"Selected 'Executive Summary' due to executive persona '{persona_role.value}' inquiring about pricing."
                )
            elif p_intent == "case_studies":
                return (
                    ResponseStrategyType.CASE_STUDY,
                    f"Selected 'Case Study' due to executive interest in proven ROI proof points."
                )
            elif p_intent == "comparison":
                return (
                    ResponseStrategyType.COMPARISON,
                    f"Selected 'Comparison' due to executive comparison intent."
                )
            else:
                return (
                    ResponseStrategyType.EXECUTIVE_SUMMARY,
                    f"Selected 'Executive Summary' for executive persona '{persona_role.value}'."
                )

        # 3. Specific Business Intents
        if p_intent == "pricing":
            return (
                ResponseStrategyType.SALES_CONVERSATION,
                f"Selected 'Sales Conversation' due to commercial pricing intent '{intent_str}'."
            )
        elif p_intent == "comparison":
            return (
                ResponseStrategyType.COMPARISON,
                f"Selected 'Comparison' due to comparative intent '{intent_str}'."
            )
        elif p_intent == "recommendation" or (goals and len(goals) > 0):
            return (
                ResponseStrategyType.RECOMMENDATION,
                f"Selected 'Recommendation' due to identified customer goals: {goals}."
            )
        elif p_intent in ["requirement_gathering", "discovery"] or stage == "Discovery":
            return (
                ResponseStrategyType.REQUIREMENTS_DISCOVERY,
                f"Selected 'Requirements Discovery' due to discovery stage/intent."
            )
        elif p_intent == "case_studies":
            return (
                ResponseStrategyType.CASE_STUDY,
                f"Selected 'Case Study' due to case study request."
            )
        elif p_intent in ["support", "problem_statement"]:
            return (
                ResponseStrategyType.TROUBLESHOOTING,
                f"Selected 'Troubleshooting' due to support/issue intent '{intent_str}'."
            )
        elif p_intent == "workflow":
            return (
                ResponseStrategyType.STEP_BY_STEP,
                f"Selected 'Step-by-Step' due to workflow procedural intent '{intent_str}'."
            )

        # 4. Fallback Default: Consultative Discussion or FAQ
        if stage == "Greeting":
            return (
                ResponseStrategyType.EDUCATIONAL,
                "Selected 'Educational' for initial conversation stage."
            )

        return (
            ResponseStrategyType.CONSULTATIVE_DISCUSSION,
            f"Selected 'Consultative Discussion' for general intent '{intent_str}'."
        )

    def plan(
        self,
        intent: IntentAnalysis,
        persona_profile: Optional[PersonaProfile],
        context: ConversationContext
    ) -> ResponsePlan:
        """
        Formulates a comprehensive ResponsePlan blueprint.
        """
        primary_intent_str = intent.primary_intent
        persona_role = persona_profile.primary_role if persona_profile else RolePersona.UNKNOWN
        stage = context.current_stage
        
        # Read goals from context variables if available
        goals = []
        if "persona_profile" in context.variables and hasattr(context.variables["persona_profile"], "turn_history"):
            pass
        if "discovery_state" in context.variables:
            disc = context.variables["discovery_state"]
            if hasattr(disc, "goals"):
                goals = disc.goals

        # 1. Select Strategy Type
        strat_type, reasoning = self.select_strategy_type(
            primary_intent_str, persona_role, stage, context.active_entity_id, goals
        )

        # 2. Retrieve Template Parameters
        template = STRATEGY_TEMPLATES[strat_type]

        target_ent = context.active_entity_id or "General Platform Solution"

        plan_obj = ResponsePlan(
            strategy_type=strat_type,
            tone=template["tone"],
            depth=template["depth"],
            sections=template["sections"],
            length=template["length"],
            follow_up=template["follow_up"],
            cta=template["cta"],
            target_entity=target_ent,
            selection_reasoning=reasoning
        )

        logger.info(
            f"ResponsePlanningEngine: Formulated plan for session {context.session_id} -> "
            f"Strategy: {strat_type.value}, Tone: {plan_obj.tone}, Sections: {len(plan_obj.sections)}"
        )

        return plan_obj


_planning_engine_instance: Optional[ResponsePlanningEngine] = None

def get_response_planning_engine() -> ResponsePlanningEngine:
    global _planning_engine_instance
    if _planning_engine_instance is None:
        _planning_engine_instance = ResponsePlanningEngine()
    return _planning_engine_instance
