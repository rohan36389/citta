import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Setup paths
BACKEND_DIR = Path(__file__).resolve().parent
TAXONOMY_DIR = BACKEND_DIR / "knowledge" / "taxonomy"

# Global cache loaded once during startup
_company_cache: Dict[str, Any] = {}
_products_cache: List[Dict[str, Any]] = []
_solutions_cache: List[Dict[str, Any]] = []
_services_cache: List[Dict[str, Any]] = []
_navigation_cache: List[Dict[str, Any]] = []
_loaded = False

def load_taxonomy():
    """Load and validate taxonomy JSON structures once on startup."""
    global _company_cache, _products_cache, _solutions_cache, _services_cache, _navigation_cache, _loaded
    if _loaded:
        return
        
    try:
        # 1. Company
        company_path = TAXONOMY_DIR / "company.json"
        if company_path.exists():
            with open(company_path, "r", encoding="utf-8") as f:
                _company_cache = json.load(f)
        else:
            logger.warning(f"company.json not found at {company_path}")
            
        # 2. Navigation
        nav_path = TAXONOMY_DIR / "navigation.json"
        if nav_path.exists():
            with open(nav_path, "r", encoding="utf-8") as f:
                _navigation_cache = json.load(f)
                
        # 3. Products
        products_path = TAXONOMY_DIR / "products.json"
        if products_path.exists():
            with open(products_path, "r", encoding="utf-8") as f:
                _products_cache = json.load(f)
                
        # 4. Solutions
        solutions_path = TAXONOMY_DIR / "solutions.json"
        if solutions_path.exists():
            with open(solutions_path, "r", encoding="utf-8") as f:
                _solutions_cache = json.load(f)
                
        # 5. Services
        services_path = TAXONOMY_DIR / "services.json"
        if services_path.exists():
            with open(services_path, "r", encoding="utf-8") as f:
                _services_cache = json.load(f)
                
        # Perform schema verification
        validate_schema()
        _loaded = True
        logger.info("Canonical Taxonomy loaded and verified successfully.")
    except Exception as e:
        logger.exception("Failed to load or validate taxonomy files")
        raise RuntimeError(f"Taxonomy loading error: {str(e)}")

def validate_schema():
    """Run verification checks on loaded taxonomy cache data."""
    product_ids = {p.get("id") for p in _products_cache if p.get("id")}
    solution_ids = {s.get("id") for s in _solutions_cache if s.get("id")}
    
    # Check no Product ID exists inside Solutions and vice-versa
    overlap = product_ids.intersection(solution_ids)
    if overlap:
        raise ValueError(f"Taxonomy overlap error: IDs found in both Products and Solutions: {overlap}")
        
    # Verify every product, solution, and service has a valid route
    for item in _products_cache:
        route = item.get("route")
        if not route or not route.startswith("/"):
            raise ValueError(f"Invalid route in product {item.get('id')}: {route}")
            
    for item in _solutions_cache:
        route = item.get("route")
        if not route or not route.startswith("/"):
            raise ValueError(f"Invalid route in solution {item.get('id')}: {route}")
            
    for item in _services_cache:
        route = item.get("route")
        if not route or not route.startswith("/"):
            raise ValueError(f"Invalid route in service {item.get('id')}: {route}")

# --- Helper Methods ---

def get_company() -> Dict[str, Any]:
    load_taxonomy()
    return _company_cache

def get_products() -> List[Dict[str, Any]]:
    load_taxonomy()
    return _products_cache

def get_solutions() -> List[Dict[str, Any]]:
    load_taxonomy()
    return _solutions_cache

def get_services() -> List[Dict[str, Any]]:
    load_taxonomy()
    return _services_cache

def get_navigation() -> List[Dict[str, Any]]:
    load_taxonomy()
    return _navigation_cache

def get_product(name_or_id: str) -> Optional[Dict[str, Any]]:
    name_clean = name_or_id.lower().replace("_", " ").replace("-", " ").strip()
    for p in get_products():
        if p["id"].lower() == name_or_id.lower():
            return p
        p_name = p["name"].lower().replace("_", " ").replace("-", " ").strip()
        if name_clean in p_name or p_name in name_clean:
            return p
    return None

def get_solution(name_or_id: str) -> Optional[Dict[str, Any]]:
    name_clean = name_or_id.lower().replace("_", " ").replace("-", " ").strip()
    for s in get_solutions():
        if s["id"].lower() == name_or_id.lower():
            return s
        s_name = s["name"].lower().replace("_", " ").replace("-", " ").strip()
        if name_clean in s_name or s_name in name_clean:
            return s
    return None

def get_service(name_or_id: str) -> Optional[Dict[str, Any]]:
    name_clean = name_or_id.lower().replace("_", " ").replace("-", " ").strip()
    for serv in get_services():
        if serv["id"].lower() == name_or_id.lower():
            return serv
        serv_name = serv["name"].lower().replace("_", " ").replace("-", " ").strip()
        if name_clean in serv_name or serv_name in name_clean:
            return serv
    return None

def find_route(name_or_id: str) -> Optional[str]:
    # Check products
    p = get_product(name_or_id)
    if p:
        return p["route"]
    # Check solutions
    s = get_solution(name_or_id)
    if s:
        return s["route"]
    # Check services
    serv = get_service(name_or_id)
    if serv:
        return serv["route"]
    # Check navigation
    name_clean = name_or_id.lower().strip()
    for nav in get_navigation():
        if nav["name"].lower() == name_clean:
            return nav["route"]
    return None

# Load immediately when module is imported
load_taxonomy()
