import re
from typing import Any, List, Optional

def clean_val(val: Any) -> str:
    """Sanitizes text fields to ensure None, null, or empty string literals are never rendered."""
    if val is None:
        return ""
    s = str(val).strip()
    if s.lower() in ["none", "null", "empty", "unknown", "none.", "null."]:
        return ""
    return s

def sanitize_conversational_text(text: str) -> str:
    """
    Transforms website-style markdown responses into clean, conversational chat responses optimized for desktop and mobile.
    Enforces Enterprise Reasoning Engine rules:
    - Strips raw navigation phrases ("Redirecting...", "Opening...", "Taking you...")
    - Ensures Click-Only Navigation (only optional Contact links)
    - Strips broken links, webpage heading artifacts, and redundant bullet dumps.
    """
    if not text:
        return ""

    t = text

    # 0. Strip forced redirection phrases (Click-Only Navigation Rule)
    t = re.sub(r"\b(redirecting|opening|taking you|navigating to)\b[^\.\n]*[\.\n]?", "", t, flags=re.IGNORECASE)

    # 1. Strip markdown links with internal URLs or action text: e.g. [View Solution →](/solutions/ecommerce-os)
    action_phrases = ["explore", "view", "learn more", "read more", "get started", "consult ai", "click here", "show"]
    
    def replace_md_link(match):
        label = match.group(1).strip()
        url = match.group(2).strip()
        label_clean = re.sub(r"[→\->=>]", "", label).strip()
        
        # Check if it's an action CTA phrase
        if any(p in label_clean.lower() for p in action_phrases):
            return ""
        # Return clean label without link syntax or arrow
        return label_clean

    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_md_link, t)

    # 2. Remove any remaining raw internal URLs or route paths (e.g., /products/..., /solutions/..., /services/..., /about, /contact)
    t = re.sub(r"/(?:products|services|solutions|case-studies|about|contact|recognition)[^\s\)]*", "", t)
    t = re.sub(r"https?://[^\s\)]*", "", t)

    # 3. Remove arrows and broken link symbols
    t = re.sub(r"[→\->=>]\s*", "", t)
    t = re.sub(r"\[\s*\]|\(\s*\)", "", t)

    # 4. Transform webpage headers (### Heading) into conversational bold headers
    t = re.sub(r"###\s*Overview\b", "**Overview**:", t, flags=re.IGNORECASE)
    t = re.sub(r"###\s*Summary\b", "**Summary**:", t, flags=re.IGNORECASE)
    t = re.sub(r"###\s*(Core Capabilities|Capabilities & Methodology|System Modules & Capabilities)\b", "**Key Highlights**:", t, flags=re.IGNORECASE)
    t = re.sub(r"###\s*(Key Benefits|Service Outcomes|Strategic Value|Client Benefits)\b", "**Core Value**:", t, flags=re.IGNORECASE)
    t = re.sub(r"###\s*(Implementation Workflow|System Architecture & Workflow)\b", "**Workflow & Mechanics**:", t, flags=re.IGNORECASE)
    t = re.sub(r"###\s*(Ideal Use Cases|Target Audience)\b", "**Target Audience**:", t, flags=re.IGNORECASE)
    t = re.sub(r"###\s*", "**", t)

    # 5. Normalize bullet points to clean '• '
    t = re.sub(r"^\s*[\-\*]\s+", "• ", t, flags=re.MULTILINE)

    # 6. Remove literal "None", "null", "undefined", "Unknown"
    t = re.sub(r"\b(None|null|undefined|Unknown)\b", "", t)

    # 7. Clean up empty lines and trailing spaces
    lines = [line.strip() for line in t.split("\n")]
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                cleaned_lines.append("")
                prev_blank = True
        else:
            cleaned_lines.append(line)
            prev_blank = False

    return "\n".join(cleaned_lines).strip()

def render_product(obj) -> str:
    """Renders a Product object to conversational chat format."""
    parts = []
    title = clean_val(obj.title or obj.name)
    tagline = clean_val(obj.tagline)
    overview = clean_val(obj.overview or obj.description)
    
    parts.append(f"🏆 **{title}**")
    if tagline:
        parts.append(f"*{tagline}*\n")
    if overview:
        parts.append(f"{overview}\n")
    
    if obj.capabilities:
        parts.append("Key Highlights:")
        for cap in obj.capabilities[:5]:
            cap_title = clean_val(cap.title)
            cap_desc = clean_val(cap.description)
            parts.append(f"• **{cap_title}**: {cap_desc}" if cap_desc else f"• **{cap_title}**")
        parts.append("")
        
    if obj.benefits:
        bens = [clean_val(b) for b in obj.benefits if clean_val(b)]
        if bens:
            parts.append("Core Value & Benefits:")
            for benefit in bens[:4]:
                parts.append(f"• {benefit}")
            parts.append("")
            
    if obj.target_users:
        users = [clean_val(u) for u in obj.target_users if clean_val(u)]
        if users:
            parts.append(f"**Target Audience**: {', '.join(users)}")
            
    return sanitize_conversational_text("\n".join(parts))

def render_service(obj) -> str:
    """Renders a Service object to conversational chat format."""
    parts = []
    title = clean_val(obj.title or obj.name)
    tagline = clean_val(obj.tagline)
    overview = clean_val(obj.overview or obj.description)

    parts.append(f"🛠️ **{title}**")
    if tagline:
        parts.append(f"*{tagline}*\n")
    if overview:
        parts.append(f"{overview}\n")
    
    if obj.capabilities:
        parts.append("Key Highlights:")
        for cap in obj.capabilities[:5]:
            c_title = clean_val(cap.title)
            c_desc = clean_val(cap.description)
            parts.append(f"• **{c_title}**: {c_desc}" if c_desc else f"• **{c_title}**")
        parts.append("")
        
    if obj.benefits:
        bens = [clean_val(b) for b in obj.benefits if clean_val(b)]
        if bens:
            parts.append("Core Value & Benefits:")
            for benefit in bens[:4]:
                parts.append(f"• {benefit}")
            parts.append("")
            
    return sanitize_conversational_text("\n".join(parts))

def render_solution(obj) -> str:
    """Renders a Solution object to conversational chat format."""
    parts = []
    title = clean_val(obj.title or obj.name)
    tagline = clean_val(obj.tagline)
    overview = clean_val(obj.overview or obj.description)

    parts.append(f"⚙️ **{title}**")
    if tagline:
        parts.append(f"*{tagline}*\n")
    if overview:
        parts.append(f"{overview}\n")
    
    if obj.capabilities:
        parts.append("Key Highlights, Process & Platform Benefits:")
        for cap in obj.capabilities[:5]:
            c_title = clean_val(cap.title)
            c_desc = clean_val(cap.description)
            parts.append(f"• **{c_title}**: {c_desc}" if c_desc else f"• **{c_title}**")
        parts.append("")
        
    if obj.workflows:
        parts.append("System Architecture & Workflow:")
        for step in obj.workflows[:4]:
            s_title = clean_val(step.title)
            s_desc = clean_val(step.description)
            parts.append(f"• Step {step.step} ({s_title}): {s_desc}" if s_desc else f"• Step {step.step}: {s_title}")
        parts.append("")

    return sanitize_conversational_text("\n".join(parts))

def render_company(obj) -> str:
    """Renders Company Info object into clean conversational chat response."""
    title = clean_val(obj.title or obj.name)

    parts = []
    parts.append(f"🏢 **{title}** is an Enterprise AI consultancy that helps organizations build secure, scalable, and production-ready AI solutions.")
    parts.append("")
    parts.append("Here is a quick overview:")
    parts.append("• Founded in 2022")
    parts.append("• Serves 50+ enterprise clients")
    parts.append("• Serves 100,000+ active enterprise users")
    parts.append("• Delivers ₹3.5 Cr+ measurable client ROI")
    parts.append("• Specializes in Enterprise AI, Data Engineering, and Industry-specific AI platforms")
    parts.append("")
    parts.append("**Mission**: To empower enterprise transformation through autonomous, transparent, and scalable AI solutions.")
    parts.append("**Vision**: To be the global benchmark for trusted Enterprise AI architecture.")
    parts.append("")
    parts.append("You can also ask about our leadership team, products, services, or case studies.")
    return "\n".join(parts)

def render_case_study(obj) -> str:
    """Renders Case Study object to conversational chat format."""
    parts = []
    title = clean_val(obj.title or obj.name)
    tagline = clean_val(obj.tagline)
    overview = clean_val(obj.overview or obj.description)

    parts.append(f"📈 **Case Study: {title}**")
    if tagline:
        parts.append(f"*{tagline}*\n")
    if overview:
        parts.append(f"{overview}\n")
        
    if obj.capabilities:
        parts.append("Key Highlights:")
        for cap in obj.capabilities[:4]:
            c_title = clean_val(cap.title)
            c_desc = clean_val(cap.description)
            if c_title and c_desc:
                parts.append(f"• **{c_title}**: {c_desc}")
        parts.append("")
                
    if obj.benefits:
        bens = [clean_val(b) for b in obj.benefits if clean_val(b)]
        if bens:
            parts.append("Core Value:")
            for b in bens[:4]:
                parts.append(f"• {b}")
            parts.append("")
            
    return sanitize_conversational_text("\n".join(parts))

def render_award(obj) -> str:
    """Renders Award object."""
    title = clean_val(obj.title or obj.name)
    desc = clean_val(obj.description or obj.overview)
    return f"🏆 **{title}**\n\n{desc}"

def render_faq(obj) -> str:
    """Renders FAQ object."""
    parts = []
    parts.append(f"❓ **{clean_val(obj.title or obj.name)}**\n")
    if obj.faq:
        for item in obj.faq[:5]:
            q = clean_val(item.question)
            a = clean_val(item.answer)
            if q and a:
                parts.append(f"**Q: {q}**\n*A: {a}*\n")
    return "\n".join(parts).strip()

def render_contact(obj) -> str:
    """Renders Contact object."""
    title = clean_val(obj.title or obj.name)
    overview = clean_val(obj.overview or obj.description)
    return f"📞 **{title}**\n\n{overview}\n\n**Address**: HITEC City, Hyderabad, Telangana, India"

def render_capability(cap_entry: dict) -> str:
    """Renders a single Capability object with context of parent entity."""
    cap = cap_entry["capability"]
    parent = cap_entry["parent"]
    
    c_title = clean_val(cap.title)
    c_desc = clean_val(cap.description)
    p_title = clean_val(parent.title)
    
    parts = []
    parts.append(f"⚡ **{c_title}**")
    parts.append(f"Part of **{p_title}** ({parent.type.value.title()})\n")
    parts.append(f"{c_desc}\n")
    
    if cap.features:
        parts.append("Key Features Included:")
        for feat in cap.features[:4]:
            f_title = clean_val(feat.title)
            f_desc = clean_val(feat.description)
            parts.append(f"• **{f_title}**: {f_desc}" if f_desc else f"• **{f_title}**")
        parts.append("")
        
    return sanitize_conversational_text("\n".join(parts))

def render_feature(feat_entry: dict) -> str:
    """Renders a single Feature object with context of capability and parent."""
    feat = feat_entry["feature"]
    cap = feat_entry["capability"]
    parent = feat_entry["parent"]
    
    f_title = clean_val(feat.title)
    f_desc = clean_val(feat.description)
    c_title = clean_val(cap.title)
    p_title = clean_val(parent.title)
    
    parts = []
    parts.append(f"✨ **{f_title}**")
    parts.append(f"Capability: **{c_title}** (Part of **{p_title}**)\n")
    parts.append(f"{f_desc}\n")
    
    return sanitize_conversational_text("\n".join(parts))

def render_target_users(obj: Any) -> str:
    """Renders target audience / intended users for any object."""
    title = clean_val(getattr(obj, "title", None) or getattr(obj, "name", None) or "CittaAI")
    users = getattr(obj, "target_users", None)
    if not users and isinstance(obj, dict):
        users = obj.get("target_users")
    if users and isinstance(users, list):
        user_str = ", ".join([clean_val(u) for u in users if clean_val(u)])
        return f"🎯 **Target Audience for {title}**:\n\n{title} is designed for **{user_str}**."
    return f"🎯 **Target Audience for {title}**:\n\n{title} is designed for Enterprises, Technical Leaders, and Decision Makers seeking production-ready AI solutions."

def render_features(obj: Any) -> str:
    """Renders feature list for an object across capabilities or features list."""
    title = clean_val(getattr(obj, "title", None) or getattr(obj, "name", None) or "CittaAI")
    feats = []
    caps = getattr(obj, "capabilities", []) or []
    for cap in caps:
        c_title = clean_val(getattr(cap, "title", ""))
        c_feats = getattr(cap, "features", []) or []
        for f in c_feats:
            f_title = clean_val(getattr(f, "title", ""))
            f_desc = clean_val(getattr(f, "description", ""))
            if f_title:
                feats.append(f"• **{f_title}** ({c_title}): {f_desc}" if (f_desc and c_title) else (f"• **{f_title}**: {f_desc}" if f_desc else f"• **{f_title}**"))
    if not feats and isinstance(obj, dict):
        raw_feats = obj.get("features", [])
        for f in raw_feats:
            if isinstance(f, dict):
                feats.append(f"• **{clean_val(f.get('title'))}**: {clean_val(f.get('description'))}")
            elif isinstance(f, str):
                feats.append(f"• {clean_val(f)}")
    if feats:
        feat_str = "\n".join(feats[:8])
        return sanitize_conversational_text(f"✨ **Key Features of {title}**\n\n{feat_str}")
    return render_by_type(obj)

def render_capabilities_list(obj: Any) -> str:
    """Renders capability list for an object."""
    title = clean_val(getattr(obj, "title", None) or getattr(obj, "name", None) or "CittaAI")
    caps = getattr(obj, "capabilities", []) or []
    if not caps and isinstance(obj, dict):
        caps = obj.get("capabilities", [])
    if caps:
        cap_bullets = []
        for cap in caps:
            if hasattr(cap, "title"):
                c_title = clean_val(cap.title)
                c_desc = clean_val(cap.description)
            elif isinstance(cap, dict):
                c_title = clean_val(cap.get("title"))
                c_desc = clean_val(cap.get("description"))
            else:
                c_title = clean_val(cap)
                c_desc = ""
            if c_title:
                cap_bullets.append(f"• **{c_title}**: {c_desc}" if c_desc else f"• **{c_title}**")
        if cap_bullets:
            cap_str = "\n".join(cap_bullets)
            return sanitize_conversational_text(f"⚡ **Capabilities Provided by {title}**\n\n{cap_str}")
    return render_by_type(obj)

def render_faq_section(obj: Any) -> str:
    """Renders FAQ section for an object."""
    title = clean_val(getattr(obj, "title", None) or getattr(obj, "name", None) or "CittaAI")
    faqs = getattr(obj, "faq", []) or []
    if not faqs and isinstance(obj, dict):
        faqs = obj.get("faq", [])
    if faqs:
        parts = [f"❓ **Frequently Asked Questions for {title}**\n"]
        for item in faqs[:5]:
            if hasattr(item, "question"):
                q = clean_val(item.question)
                a = clean_val(item.answer)
            elif isinstance(item, dict):
                q = clean_val(item.get("question"))
                a = clean_val(item.get("answer"))
            else:
                continue
            if q and a:
                parts.append(f"**Q: {q}**\n*A: {a}*\n")
        return "\n".join(parts).strip()
    return render_by_type(obj)

def render_pricing_section(obj: Any) -> str:
    """Renders pricing section for an object."""
    title = clean_val(getattr(obj, "title", None) or getattr(obj, "name", None) or "CittaAI")
    return (
        f"💳 **Pricing & Licensing for {title}**\n\n"
        f"CittaAI offers customized enterprise licensing and transparent annual subscriptions for **{title}** based on deployable modules, volume, and SLA tier requirements.\n\n"
        f"• **Starter / Pilot Tier**: Fixed-fee PoC deployment.\n"
        f"• **Enterprise Tier**: Annual subscription with 99.9% uptime SLA.\n"
        f"• **Custom Advisory**: Time-and-materials or milestone-based consulting.\n\n"
        f"Contact our team to get a detailed quote tailored to your architecture."
    )

def render_relationships_section(obj: Any) -> str:
    """Renders linked entities / related services section."""
    title = clean_val(getattr(obj, "title", None) or getattr(obj, "name", None) or "CittaAI")
    rels = getattr(obj, "relationships", []) or []
    if not rels and isinstance(obj, dict):
        rels = obj.get("relationships", [])
    if rels:
        rel_str = ", ".join([clean_val(r.target if hasattr(r, "target") else r.get("target")) for r in rels if r])
        return f"🔗 **Related Offerings for {title}**:\n\n{title} integrates cleanly with: **{rel_str}**."
    return f"🔗 **Related Offerings for {title}**:\n\n{title} seamlessly connects with CittaAI Data Engineering and Enterprise AI OS middleware."

def render_section(obj: Any, section: str) -> str:
    """Renders specific section for an object."""
    sec = (section or "").lower().strip()
    if sec in ["best_for", "target", "audience", "industries", "target_audience"]:
        return render_target_users(obj)
    if sec in ["how_it_works", "workflow", "workflows", "process"]:
        workflows = getattr(obj, "workflows", [])
        if not workflows and isinstance(obj, dict):
            workflows = obj.get("workflows", [])
        title = clean_val(getattr(obj, "title", None) or getattr(obj, "name", None) or "CittaAI")
        steps = []
        if workflows:
            for step in workflows:
                if hasattr(step, "step"):
                    steps.append(f"Step {step.step}. **{clean_val(step.title)}**: {clean_val(step.description)}")
                else:
                    steps.append(f"Step {step.get('step', '')}. **{clean_val(step.get('title'))}**: {clean_val(step.get('description'))}")
        else:
            caps = getattr(obj, "capabilities", []) or []
            for idx, cap in enumerate(caps[:4], 1):
                c_title = clean_val(getattr(cap, "title", None) if hasattr(cap, "title") else (cap.get("title") if isinstance(cap, dict) else str(cap)))
                c_desc = clean_val(getattr(cap, "description", None) if hasattr(cap, "description") else (cap.get("description") if isinstance(cap, dict) else ""))
                steps.append(f"Step {idx}. **{c_title}**: {c_desc}" if c_desc else f"Step {idx}. **{c_title}**")
        if steps:
            wf_str = "\n".join(steps)
            return sanitize_conversational_text(f"⚙️ **System Workflow & Architecture for {title}**\n\n{wf_str}")
    if sec in ["benefits", "benefit", "advantages"]:
        benefits = getattr(obj, "benefits", [])
        if not benefits and isinstance(obj, dict):
            benefits = obj.get("benefits", [])
        title = clean_val(getattr(obj, "title", None) or getattr(obj, "name", None) or "CittaAI")
        ben_bullets = []
        if benefits:
            ben_bullets = [f"• {clean_val(b)}" for b in benefits if clean_val(b)]
        else:
            caps = getattr(obj, "capabilities", []) or []
            for cap in caps[:5]:
                c_title = clean_val(getattr(cap, "title", None) if hasattr(cap, "title") else (cap.get("title") if isinstance(cap, dict) else str(cap)))
                c_desc = clean_val(getattr(cap, "description", None) if hasattr(cap, "description") else (cap.get("description") if isinstance(cap, dict) else ""))
                if c_title:
                    ben_bullets.append(f"• **{c_title}**: {c_desc}" if c_desc else f"• **{c_title}**")
        if ben_bullets:
            b_str = "\n".join(ben_bullets)
            return sanitize_conversational_text(f"### Key Benefits of {title}\n\n{b_str}")
    if sec in ["features", "modules", "functions"]:
        return render_features(obj)
    if sec in ["capabilities", "capability"]:
        return render_capabilities_list(obj)
    if sec in ["faq", "faqs", "questions"]:
        return render_faq_section(obj)
    if sec in ["pricing", "price", "cost"]:
        return render_pricing_section(obj)
    if sec in ["related_entities", "relationships", "related"]:
        return render_relationships_section(obj)
    if sec in ["contact", "address"]:
        return render_contact(obj)
    return render_by_type(obj)

def render_by_type(obj: Any) -> str:
    """Helper dispatcher to render any schema object by KnowledgeType."""
    t = obj.type.value
    if t == "product":
        return render_product(obj)
    elif t == "service":
        return render_service(obj)
    elif t == "solution":
        return render_solution(obj)
    elif t == "company":
        return render_company(obj)
    elif t == "case_study":
        return render_case_study(obj)
    elif t == "award":
        return render_award(obj)
    elif t == "faq":
        return render_faq(obj)
    elif t == "contact":
        return render_contact(obj)
    else:
        return f"**{clean_val(obj.title)}**\n{clean_val(obj.description)}"
