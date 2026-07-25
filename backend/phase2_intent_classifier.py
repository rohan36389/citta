import re
import logging
from typing import Dict, Any, List, Optional
from orchestration_context import EnterpriseIntent

logger = logging.getLogger(__name__)

INTENT_PATTERNS: Dict[str, List[str]] = {
    EnterpriseIntent.SCHEDULE_DEMO.value: [
        r"\bschedule\s+(a\s+)?(product\s+)?demo\b", r"\bbook\s+(a\s+)?demo\b", r"\bschedule\s+meeting\b", r"\bbook\s+meeting\b"
    ],
    EnterpriseIntent.CREATE_TICKET.value: [
        r"\bcreate\s+(a\s+)?(support\s+)?ticket\b", r"\braise\s+(a\s+)?ticket\b", r"\bopen\s+(a\s+)?ticket\b", r"\bsubmit\s+ticket\b"
    ],
    EnterpriseIntent.SEND_PROPOSAL.value: [
        r"\bsend\s+proposal\b", r"\bemail\s+proposal\b", r"\bgenerate\s+proposal\b"
    ],
    EnterpriseIntent.EXECUTE_ACTION.value: [
        r"\bupdate\s+erp\b", r"\bexecute\s+action\b", r"\bperform\s+action\b"
    ],
    EnterpriseIntent.COMPARISON.value: [
        r"\bcompare\b", r"\bvs\.?\b", r"\bversus\b", r"\bdifference\b", r"\bdifferences\b",
        r"\bdistinguish\b", r"\bcomparison\b", r"\bhow\s+does\s+.*compare\b"
    ],
    EnterpriseIntent.RECOMMENDATION.value: [
        r"\brecommend\b", r"\bsuggest\b", r"\bwhich\s+solution\b", r"\bwhich\s+product\b",
        r"\bwhich\s+service\b", r"\bwhich\s+one\s+should\b", r"\bwhat\s+should\s+we\s+choose\b",
        r"\bbest\s+solution\b", r"\bbest\s+product\b", r"\bbest\s+service\b", r"\bhelp\s+us\s+choose\b",
        r"\bwe\s+are\s+a\b"
    ],
    EnterpriseIntent.SUITABILITY.value: [
        r"\bwhy\s+is\s+.*better\b", r"\b(is|would|will)\s+.*suit(able)?\b", r"\bsuitable\b", r"\bsuitability\b",
        r"\bwhy\s+choose\b", r"\bwhy\s+use\b", r"\bbetter\s+than\b", r"\balternative\s+to\b", r"\bsuit\b"
    ],
    EnterpriseIntent.INTEGRATION.value: [
        r"\bintegrat(e|ion|ions)\b", r"\bconnect\b", r"\bcrm\b", r"\berp\b", r"\bshopify\b", r"\bapi\b", r"\bwebhooks\b"
    ],
    EnterpriseIntent.IMPLEMENTATION.value: [
        r"\bimplement(ation)?\b", r"\bdeploy(ment)?\b", r"\bsetup\b", r"\bonboard(ing)?\b", r"\binstall(ation)?\b"
    ],
    EnterpriseIntent.WORKFLOW.value: [
        r"\bhow\s+does\s+.*work\b", r"\bhow\s+it\s+works\b", r"\bworkflow\b", r"\bprocess\b",
        r"\bworking\b", r"\barchitecture\b", r"\bflow\b", r"\bworkings\b", r"\bhow\s+to\s+use\b"
    ],
    EnterpriseIntent.BENEFITS.value: [
        r"\bbenefits?\b", r"\badvantages?\b", r"\bvalue\s+proposition\b", r"\broi\b", r"\bwhy\s+should\b"
    ],
    EnterpriseIntent.FEATURES.value: [
        r"\bfeatures?\b", r"\bmodules?\b", r"\bfunctions?\b", r"\bcomponents?\b", r"\bspecs?\b"
    ],
    EnterpriseIntent.CAPABILITIES.value: [
        r"\bcapabilities\b", r"\bwhat\s+capabilities\b", r"\bwhat\s+can\s+it\s+do\b", r"\babilities\b"
    ],
    EnterpriseIntent.PRICING.value: [
        r"\bpricing\b", r"\bcost\b", r"\bprice\b", r"\bquote\b", r"\bplans\b", r"\bcharge\b", r"\bsubscription\b"
    ],
    EnterpriseIntent.CONTACT.value: [
        r"\bcontact\b", r"\bphone\b", r"\bemail\b", r"\breach\b", r"\boffice\b", r"\blocation\b", r"\baddress\b"
    ],
    EnterpriseIntent.INDUSTRIES.value: [
        r"\bindustr(y|ies)\b", r"\bverticals?\b", r"\bsectors?\b", r"\bdomains?\b"
    ],
    EnterpriseIntent.TARGET_AUDIENCE.value: [
        r"\btarget\s+audience\b", r"\bwho\s+is\s+it\s+for\b", r"\bwho\s+should\s+use\b", r"\bwho\s+uses\b", r"\bideal\s+for\b", r"\bintended\s+users\b"
    ],
    EnterpriseIntent.FAQ.value: [
        r"\bfaq\b", r"\bfaqs\b", r"\bquestions?\b", r"\bq&a\b"
    ],
    EnterpriseIntent.RELATIONSHIPS.value: [
        r"\brelated\b", r"\bdependencies\b", r"\brelationship\b", r"\bconnects\s+to\b"
    ],
    EnterpriseIntent.USE_CASE.value: [
        r"\buse\s+cases?\b", r"\bcase\s+stud(y|ies)\b", r"\bexamples?\b", r"\bsample\b", r"\bsuccess\s+stor(y|ies)\b"
    ],
    EnterpriseIntent.LIST.value: [
        r"\blist\b", r"\bshow\s+all\b", r"\bwhat\s+products\b", r"\bwhat\s+services\b", r"\bwhat\s+solutions\b",
        r"\bwhat\s+do\s+you\s+offer\b", r"\bavailable\s+solutions\b"
    ],
    EnterpriseIntent.CLASSIFICATION.value: [
        r"\bwhat\s+kind\s+of\b", r"\bwhat\s+category\b", r"\bis\s+it\s+a\s+product\b", r"\bis\s+it\s+a\s+service\b"
    ],
    EnterpriseIntent.OVERVIEW.value: [
        r"\btell\s+me\s+about\b", r"\boverview\b", r"\bdescribe\b", r"\bwhat\s+is\b", r"\bwhat\s+are\b", r"\babout\b", r"\bexplain\b"
    ]
}

class Phase2IntentClassifier:
    def __init__(self):
        pass

    def classify(self, query: str) -> str:
        q_lower = query.lower().strip()

        for intent_name, patterns in INTENT_PATTERNS.items():
            for p in patterns:
                if re.search(p, q_lower):
                    return intent_name

        return EnterpriseIntent.OVERVIEW.value

_classifier_instance = None

def get_phase2_intent_classifier() -> Phase2IntentClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = Phase2IntentClassifier()
    return _classifier_instance
