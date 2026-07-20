import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent

class TenantConfig:
    def __init__(self, tenant_id: str, data: Dict[str, Any]):
        self.tenant_id = tenant_id
        self.name = data.get("name", "Enterprise Platform")
        self.website_url = data.get("website_url", "https://cittaai.com")
        self.logo_url = data.get("logo_url", "")
        self.contact_email = data.get("contact_email", "info@cittaai.com")
        self.contact_phone = data.get("contact_phone", "+91 9392655040")
        self.brand_color = data.get("brand_color", "#4F46E5")
        self.brand_tagline = data.get("brand_tagline", "Elevate. Innovate. Captivate.")
        self.routes = data.get("routes", {
            "about": "/about",
            "contact": "/contact",
            "products": "/products",
            "services": "/services",
            "solutions": "/solutions",
            "case_studies": "/case-studies",
            "recognition": "/recognition"
        })

class TenantRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TenantRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.tenants: Dict[str, TenantConfig] = {}
        self._register_default_tenants()

    def _register_default_tenants(self):
        # Tenant #1: CittaAI
        cittaai_config = TenantConfig("cittaai", {
            "name": "CittaAI",
            "website_url": "https://cittaai.com",
            "logo_url": "/assets/cittaai_logo.svg",
            "contact_email": "info@cittaai.com",
            "contact_phone": "+91 9392655040",
            "brand_color": "#00E5FF",
            "brand_tagline": "Elevate. Innovate. Captivate.",
            "routes": {
                "about": "/about",
                "contact": "/contact",
                "products": "/products/whatsapp-marketing",
                "services": "/services",
                "solutions": "/solutions/ecommerce-os",
                "case_studies": "/case-studies",
                "recognition": "/recognition"
            }
        })
        self.tenants["cittaai"] = cittaai_config
        logger.info("Registered Tenant #1: CittaAI (cittaai)")

    def get_tenant(self, tenant_id: str = "cittaai") -> TenantConfig:
        tenant_id = (tenant_id or "cittaai").lower()
        if tenant_id not in self.tenants:
            # Fallback to cittaai if requested tenant not registered yet
            return self.tenants.get("cittaai")
        return self.tenants[tenant_id]

    def register_tenant(self, tenant_id: str, tenant_data: Dict[str, Any]) -> TenantConfig:
        tenant_id = tenant_id.lower().strip()
        config_obj = TenantConfig(tenant_id, tenant_data)
        self.tenants[tenant_id] = config_obj
        logger.info(f"Dynamically registered Tenant '{tenant_id}': {config_obj.name}")
        return config_obj

    def list_tenants(self) -> List[Dict[str, Any]]:
        return [
            {
                "tenant_id": t.tenant_id,
                "name": t.name,
                "website_url": t.website_url,
                "logo_url": t.logo_url
            }
            for t in self.tenants.values()
        ]

def get_tenant_registry() -> TenantRegistry:
    return TenantRegistry()
