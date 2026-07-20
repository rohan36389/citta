import os
import re
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Paths relative to backend directory
BACKEND_DIR = Path(__file__).parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
CONTENT_JS_PATH = FRONTEND_DIR / "src" / "data" / "content.js"

_cached_raw_data = None
_cached_mtime = None
_cached_static_data = None

def get_raw_content() -> Dict[str, Any]:
    global _cached_raw_data, _cached_mtime
    if not CONTENT_JS_PATH.exists():
        logger.error(f"content.js not found at {CONTENT_JS_PATH}")
        return {}
    
    mtime = os.path.getmtime(CONTENT_JS_PATH)
    if _cached_mtime == mtime and _cached_raw_data is not None:
        return _cached_raw_data

    try:
        with open(CONTENT_JS_PATH, "r", encoding="utf-8") as f:
            js_code = f.read()

        # Replace ES module exports with commonjs exports
        js_code = re.sub(r"export\s+const\s+", "const ", js_code)
        
        exports_list = ["BRAND", "CONTACT", "NAV", "HOMEPAGE", "PAGE_CONFIGS", "RECOGNITION", "CASESTUDIES", "ABOUT", "CONTACT_PAGE", "FOOTER"]
        exports_str = ", ".join(exports_list)
        js_code += f"\nmodule.exports = {{ {exports_str} }};\n"
        
        temp_file = BACKEND_DIR / "temp_content.cjs"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(js_code)
            
        try:
            cmd = ["node", "-e", "console.log(JSON.stringify(require('./temp_content.cjs')))"]
            result = subprocess.run(cmd, cwd=BACKEND_DIR, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            _cached_raw_data = data
            _cached_mtime = mtime
            return data
        finally:
            if temp_file.exists():
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
    except Exception as e:
        logger.exception("Failed to parse content.js dynamically")
        return {}

def get_static_data() -> Dict[str, Any]:
    global _cached_static_data, _cached_raw_data, _cached_mtime
    
    # Reload raw content if needed
    raw = get_raw_content()
    if not raw:
        return {}
        
    mtime = os.path.getmtime(CONTENT_JS_PATH) if CONTENT_JS_PATH.exists() else None
    if _cached_static_data is not None and _cached_mtime == mtime:
        return _cached_static_data
        
    brand = raw.get("BRAND", {})
    contact = raw.get("CONTACT", {})
    nav = raw.get("NAV", {})
    about = raw.get("ABOUT", {})
    footer = raw.get("FOOTER", {})
    
    # Extract social links
    social_links = {}
    for s in footer.get("socials", []):
        label = s.get("l", "").lower()
        if "linkedin" in label:
            social_links["linkedin"] = s.get("href", "#")
        elif "instagram" in label:
            social_links["instagram"] = s.get("href", "#")
        elif "twitter" in label or "x" in label:
            social_links["twitter"] = s.get("href", "#")
        elif "youtube" in label:
            social_links["youtube"] = s.get("href", "#")
            
    # Extract routes from NAV
    nav_routes = []
    service_routes = []
    product_routes = []
    
    primary_nav = nav.get("primary", [])
    for item in primary_nav:
        if "to" in item:
            nav_routes.append(item["to"])
        if "children" in item:
            for child in item["children"]:
                if "to" in child:
                    nav_routes.append(child["to"])
                    label = item.get("label", "").lower()
                    if "product" in label or "solution" in label:
                        product_routes.append(child["to"])
                    elif "service" in label:
                        service_routes.append(child["to"])
                        
    # Extract leadership and founders
    leaders = about.get("team", {}).get("leaders", [])
    others = about.get("team", {}).get("others", [])
    
    leadership_names = [l.get("name") for l in leaders if l.get("name")]
    all_team_names = leadership_names + [o.get("name") for o in others if o.get("name")]
    
    founders = []
    for l in leaders:
        title = l.get("title", "").lower()
        if "founder" in title:
            founders.append(l.get("name"))
            
    # Core values
    core_values = []
    for p in about.get("principles", []):
        core_values.append({"title": p.get("t"), "description": p.get("d")})
    for w in about.get("why", []):
        core_values.append({"title": w.get("t"), "description": w.get("d")})

    # Construct clean static dataset
    address = contact.get("address", "")
    google_maps = ""
    if address:
        google_maps = f"https://www.google.com/maps/search/?api=1&query={address.replace(' ', '+')}"

    res_data = {
        "company_name": brand.get("name", "CittaAI"),
        "email": contact.get("email", ""),
        "phone": contact.get("phone", ""),
        "address": address,
        "google_maps": google_maps,
        "social_links": social_links,
        "pages": {
            "contact": "/contact",
            "about": "/about",
            "recognition": "/recognition",
            "case_studies": "/case-studies"
        },
        "mission": about.get("lead", ""),
        "vision": brand.get("positioning", "") or brand.get("tagline", ""),
        "core_values": core_values,
        "business_hours": contact.get("hours", ""),
        "founders": founders,
        "leadership": leadership_names,
        "all_team": all_team_names,
        "navigation_routes": list(set(nav_routes)),
        "service_routes": list(set(service_routes)),
        "product_routes": list(set(product_routes)),
        "recognition_routes": ["/recognition"],
        "case_study_routes": ["/case-studies"]
    }
    _cached_static_data = res_data
    return res_data

def get_static_response(intent: str) -> Dict[str, Any]:
    sd = get_static_data()
    if not sd:
        return {}
    
    company_name = sd.get("company_name", "CittaAI")
    email = sd.get("email", "")
    phone = sd.get("phone", "")
    address = sd.get("address", "")
    gmaps = sd.get("google_maps", "")
    hours = sd.get("business_hours", "")
    mission = sd.get("mission", "")
    vision = sd.get("vision", "")
    socials = sd.get("social_links", {})
    
    if intent == "CONTACT":
        text = (
            f"**Contact {company_name}**\n\n"
            f"- **Phone**: {phone}\n"
            f"- **Email**: {email}\n"
            f"- **Address**: {address}\n\n"
            f"Feel free to visit our Contact page to get in touch!"
        )
        return {
            "type": "contact",
            "text": text,
            "redirect": "/contact",
            "suggested_questions": ["What are your business hours?", "Where is your office located?"]
        }
    elif intent == "LOCATION":
        text = (
            f"**{company_name} Headquarters Location**\n\n"
            f"**Address**: {address}\n\n"
            f"You can view our office location on [Google Maps]({gmaps})."
        )
        return {
            "type": "location",
            "text": text,
            "redirect": "/contact",
            "suggested_questions": ["How can I contact CittaAI?", "What are your business hours?"]
        }
    elif intent == "BUSINESS HOURS":
        text = (
            f"**{company_name} Business Hours**\n\n"
            f"We are open: **{hours}**.\n\n"
            f"We typically respond to inquiries within 24 hours during business hours."
        )
        return {
            "type": "business_hours",
            "text": text,
            "redirect": "/contact",
            "suggested_questions": ["How can I contact CittaAI?", "Where is CittaAI located?"]
        }
    elif intent == "SOCIAL LINKS":
        links_str = "\n".join([f"- **{k.capitalize()}**: [{k.capitalize()}]({v})" for k, v in socials.items() if v])
        text = (
            f"**{company_name} Social Media Channels**\n\n"
            f"Connect with us on our official profiles:\n{links_str}"
        )
        return {
            "type": "social_links",
            "text": text,
            "suggested_questions": ["How can I contact CittaAI?", "What is CittaAI's mission?"]
        }
    elif intent == "ABOUT":
        text = (
            f"**About {company_name}**\n\n"
            f"{company_name} is an **{vision}**.\n\n"
            f"- **Mission**: {mission}\n"
            f"- **Vision**: {vision}\n\n"
            f"You can learn more about our team and journey on our About page."
        )
        return {
            "type": "about",
            "text": text,
            "redirect": "/about",
            "suggested_questions": ["Who is the founder of CittaAI?", "What products does CittaAI offer?"]
        }
    elif intent == "LEGAL":
        text = (
            f"**{company_name} Legal & Compliance**\n\n"
            f"We are committed to security, privacy, and regulatory compliance:\n"
            f"- **Compliance Alignment**: Aligned with ISO, Startup India, and MSME frameworks.\n"
            f"- **Data Safety**: We implement enterprise-grade SOC2 and HIPAA-aligned security controls.\n"
            f"- **Policies**: Read our Privacy Policy, Terms of Service, and Security documentation on our site.\n\n"
            f"Please visit our Contact page to write to our legal team if you have any questions."
        )
        return {
            "type": "legal",
            "text": text,
            "redirect": "/contact",
            "suggested_questions": ["Is CittaAI ISO certified?", "How does CittaAI protect data?"]
        }
    elif intent == "CAREERS":
        text = (
            f"**Careers at {company_name}**\n\n"
            f"We are always looking for visionary AI engineers, operators, and strategists to build autonomous systems.\n"
            f"- **To Apply**: Submit your resume to **{email}** specifying your background.\n"
            f"- **Inquiry Type**: Select 'Careers' in our contact form.\n\n"
            f"Join us in engineering research-grade intelligence at enterprise scale."
        )
        return {
            "type": "careers",
            "text": text,
            "redirect": "/contact",
            "suggested_questions": ["What is CittaAI's email address?", "Who is on the leadership team?"]
        }
    elif intent == "CONSULTATION":
        text = (
            f"**Schedule a Strategy Call & Consultation**\n\n"
            f"Ready to deploy production-grade agentic AI? Let's discuss your goals.\n"
            f"- **Phone**: {phone}\n"
            f"- **Email**: {email}\n\n"
            f"Choose the 'Product Demo' or 'Partnership' options on our contact form to schedule an appointment."
        )
        return {
            "type": "consultation",
            "text": text,
            "redirect": "/contact",
            "suggested_questions": ["How can I contact CittaAI?", "What products do you offer?"]
        }
    elif intent == "COMPARISON":
        text = (
            f"**{company_name} vs. Traditional Vendors**\n\n"
            f"Unlike traditional software agencies or simple tool vendors:\n"
            f"- **Long-Term Partner**: We work as a unified unit, embedding with your team to ensure successful cultural adoption.\n"
            f"- **Agentic-First**: Every solution we build is designed for cognitive autonomy and real-world execution.\n"
            f"- **Battle-Tested**: Creators of robust industry operating systems (Pharma, E-Commerce, Smart Cities, LMS) engineered for strict compliance and ROI."
        )
        return {
            "type": "comparison",
            "text": text,
            "redirect": "/about",
            "suggested_questions": ["Tell me about the Pharma OS.", "What is the Enterprise AI OS?"]
        }
    return {}

def execute_tool(tool_name: str) -> Dict[str, Any]:
    raw = get_raw_content()
    if not raw:
        return {}
        
    company_name = raw.get("BRAND", {}).get("name", "CittaAI")
    
    if tool_name == "list_services":
        # Parse HOMEPAGE services items
        services_data = raw.get("HOMEPAGE", {}).get("services", {})
        lead = services_data.get("lead", "End-to-end AI transformation capabilities.")
        items = services_data.get("items", [])
        
        lines = [f"**Services Offered by {company_name}**\n", lead, ""]
        for it in items:
            title = it.get("title", "")
            sub = it.get("sub", "")
            desc = it.get("desc", "")
            to = it.get("to", "")
            lines.append(f"- **{title}** ({sub}): {desc} [View Details]({to})")
            
        text = "\n".join(lines)
        return {
            "type": "services_list",
            "text": text,
            "redirect": "/services",
            "suggested_questions": [
                "Tell me about Data Engineering.",
                "Explain Enterprise & Agentic AI services.",
                "What is your AI Strategy & Advisory service?"
            ]
        }
        
    elif tool_name == "list_products":
        # Parse HOMEPAGE products list
        products_data = raw.get("HOMEPAGE", {}).get("products", {})
        lead = products_data.get("lead", "Specialized AI platforms engineered to solve complex vertical challenges.")
        items = products_data.get("items", [])
        
        lines = [f"**{company_name} Product Ecosystem**\n", lead, ""]
        for it in items:
            title = it.get("title", "")
            desc = it.get("desc", "")
            to = it.get("to", "")
            lines.append(f"- **{title}**: {desc} [Explore Product]({to})")
            
        text = "\n".join(lines)
        return {
            "type": "products_list",
            "text": text,
            "redirect": "/products/whatsapp-marketing",
            "suggested_questions": [
                "What is the WhatsApp Marketing Platform?",
                "Tell me about the Influencer Marketing Platform.",
                "How does CittaAI attribute influencer campaign revenue?"
            ]
        }
        
    elif tool_name == "list_case_studies":
        # Parse CASESTUDIES
        case_studies = raw.get("CASESTUDIES", {})
        cases = case_studies.get("cases", [])
        
        lines = [f"**{company_name} Proven Case Studies & Results**\n", "We engineer measurable outcomes in the real world:\n"]
        for c in cases:
            brand = c.get("brand", "")
            metric = c.get("metric", "")
            label = c.get("label", "")
            desc = c.get("desc", "")
            lines.append(f"- **{brand}**: Achieved **{metric}** ({label}) - {desc}")
            
        text = "\n".join(lines)
        return {
            "type": "case_studies_list",
            "text": text,
            "redirect": "/case-studies",
            "suggested_questions": [
                "How did the Jewellery Brand achieve ₹3.5 Cr+?",
                "Tell me about the Spices Export case study.",
                "What is your FMCG Brand result?"
            ]
        }
        
    elif tool_name == "list_recognition":
        # Parse RECOGNITION
        recognition = raw.get("RECOGNITION", {})
        awards = recognition.get("awards", [])
        
        lines = [f"**{company_name} Awards & Recognition**\n", "Celebrating excellence and digital transformation:\n"]
        for a in awards:
            name = a.get("name", "")
            subtitle = a.get("subtitle", "")
            body = a.get("body", "")
            org = a.get("org", "")
            lines.append(f"- **{name}** ({subtitle}): {body} Organized by {org}.")
            
        text = "\n".join(lines)
        return {
            "type": "recognition_list",
            "text": text,
            "redirect": "/recognition",
            "suggested_questions": [
                "Tell me about the AP MSME 2025 Victory.",
                "What is the Best AI Startup of the Year award?"
            ]
        }
        
    return {}

def search_services() -> Dict[str, Any]:
    return execute_tool("list_services")

def search_products() -> Dict[str, Any]:
    return execute_tool("list_products")

def search_case_studies() -> Dict[str, Any]:
    return execute_tool("list_case_studies")

def search_recognition() -> Dict[str, Any]:
    return execute_tool("list_recognition")
