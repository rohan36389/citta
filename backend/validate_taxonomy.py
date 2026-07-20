import os
import sys
import json
import sqlite3
from taxonomy import get_products, get_solutions, get_services, get_navigation
from static_data import get_static_data

def validate():
    print("=== CITTAAI TAXONOMY VALIDATION ENGINE ===")
    errors = []
    warnings = []
    
    # 1. Load data
    products = get_products()
    solutions = get_solutions()
    services = get_services()
    nav = get_navigation()
    static_data = get_static_data()
    
    # Extract existing routes from content.js
    web_routes = set(static_data.get("navigation_routes", []))
    # Add service routes and product routes
    web_routes.update(static_data.get("service_routes", []))
    web_routes.update(static_data.get("product_routes", []))
    web_routes.update(["/", "/contact", "/about", "/recognition", "/case-studies", "/services"])
    
    # 2. Check overlap between products and solutions
    prod_ids = {p["id"] for p in products}
    sol_ids = {s["id"] for s in solutions}
    overlap = prod_ids.intersection(sol_ids)
    if overlap:
        errors.append(f"Overlap Error: IDs exist in both products and solutions: {overlap}")
    else:
        print("[PASS] No ID overlap between products and solutions.")
        
    # 3. Verify routes
    for p in products:
        route = p.get("route")
        if not route:
            errors.append(f"Route Error: Product '{p['id']}' has no route.")
        elif route not in web_routes:
            errors.append(f"Route Error: Product '{p['id']}' route '{route}' does not exist in content.js website navigation.")
            
    for s in solutions:
        route = s.get("route")
        if not route:
            errors.append(f"Route Error: Solution '{s['id']}' has no route.")
        elif route not in web_routes:
            errors.append(f"Route Error: Solution '{s['id']}' route '{route}' does not exist in content.js website navigation.")
            
    for serv in services:
        route = serv.get("route")
        if not route:
            errors.append(f"Route Error: Service '{serv['id']}' has no route.")
        elif route not in web_routes:
            errors.append(f"Route Error: Service '{serv['id']}' route '{route}' does not exist in content.js website navigation.")

    print(f"[INFO] Verified routes against {len(web_routes)} web pathways.")

    # 4. Check indexed knowledge in Vector Store
    db_path = os.path.join(os.path.dirname(__file__), "vector_store.db")
    chunk_counts = {}
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT metadata FROM chunks")
            for row in cursor.fetchall():
                try:
                    meta = json.loads(row[0])
                    page = meta.get("page") or meta.get("url")
                    if page:
                        chunk_counts[page] = chunk_counts.get(page, 0) + 1
                except Exception:
                    pass
            conn.close()
        except Exception as e:
            errors.append(f"DB Error: Failed to query vector store: {e}")
    else:
        warnings.append("DB Warning: vector_store.db not found on filesystem. Skipping chunk count validation.")
        
    for p in products:
        route = p["route"]
        c_count = chunk_counts.get(route, 0)
        if c_count == 0:
            warnings.append(f"Knowledge Warning: Product '{p['id']}' has 0 chunks indexed in the vector store.")
            
    for s in solutions:
        route = s["route"]
        c_count = chunk_counts.get(route, 0)
        if c_count == 0:
            warnings.append(f"Knowledge Warning: Solution '{s['id']}' has 0 chunks indexed in the vector store.")
            
    for serv in services:
        route = serv["route"]
        c_count = chunk_counts.get(route, 0)
        if c_count == 0 and serv["id"] not in ["data_engineering", "ai_strategy"]:
            warnings.append(f"Knowledge Warning: Service '{serv['id']}' has 0 chunks indexed in the vector store.")

    # 5. Output report
    print("\n=== VALIDATION SUMMARY ===")
    print(f"Total Products Checked: {len(products)}")
    print(f"Total Solutions Checked: {len(solutions)}")
    print(f"Total Services Checked: {len(services)}")
    print(f"Errors Found: {len(errors)}")
    print(f"Warnings Found: {len(warnings)}")
    
    # Write validation report to markdown file
    md_lines = [
        "# Taxonomy Validation Report",
        "",
        "## Statistics",
        f"- **Products Checked**: {len(products)}",
        f"- **Solutions Checked**: {len(solutions)}",
        f"- **Services Checked**: {len(services)}",
        f"- **Errors**: {len(errors)}",
        f"- **Warnings**: {len(warnings)}",
        "",
        "## Validation Checks"
    ]
    
    if errors:
        md_lines.append("### ❌ Errors")
        for err in errors:
            md_lines.append(f"- {err}")
            print(f"[ERROR] {err}")
    else:
        md_lines.append("###  Validation Checks Succeeded")
        md_lines.append("- [x] No overlap between products and solutions.")
        md_lines.append("- [x] Every taxonomy item has a valid, existing route.")
        print("[PASS] Every route is valid and mapped.")
        
    if warnings:
        md_lines.append("### ⚠️ Warnings")
        for warn in warnings:
            md_lines.append(f"- {warn}")
            print(f"[WARNING] {warn}")
            
    md_report_path = os.path.join(os.path.dirname(__file__), "taxonomy_validation_report.md")
    with open(md_report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"\nMarkdown report written to {md_report_path}")
    
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    validate()
