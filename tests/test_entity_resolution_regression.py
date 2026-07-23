import os
import sys
import unittest

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import config
from knowledge_registry import get_registry
import core.entity_resolver as core_resolver
from registry_resolver import resolve_registry

class TestEntityResolutionRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Force flag to True for testing the new resolver
        config.USE_NEW_ENTITY_RESOLVER = True
        cls.registry = get_registry()

    def test_registry_diagnostics_on_startup(self):
        # Check that registry successfully loaded and validated
        self.assertIsNotNone(self.registry.entities)
        self.assertIn("company_info", self.registry.entities)
        self.assertTrue(len(self.registry.entity_lookup) > 0)
        self.assertTrue(len(self.registry.alias_lookup) > 0)
        self.assertTrue(len(self.registry.slug_lookup) > 0)
        self.assertTrue(len(self.registry.keyword_lookup) > 0)

    def test_exact_canonical_id_resolutions(self):
        # Exact Canonical IDs
        test_cases = [
            ("whatsapp_marketing", "whatsapp_marketing"),
            ("influencer_marketing", "influencer_marketing"),
            ("ecommerce_os", "ecommerce_os"),
            ("pharma_os", "pharma_os"),
            ("company_info", "company_info"),
            ("founder", "founder")
        ]
        for query, expected_id in test_cases:
            res = core_resolver.resolve(query)
            self.assertEqual(res["entity_id"], expected_id, f"Failed for exact ID: {query}")
            self.assertEqual(res["confidence_level"], "EXACT")

    def test_exact_alias_resolutions(self):
        # Exact Aliases defined in registries
        test_cases = [
            ("whatsapp marketing platform", "whatsapp_marketing"),
            ("influencer marketing platform", "influencer_marketing"),
            ("e-commerce os", "ecommerce_os"),
            ("retail os", "ecommerce_os"),
            ("pharma & healthcare os", "pharma_os")
        ]
        for query, expected_id in test_cases:
            res = core_resolver.resolve(query)
            self.assertEqual(res["entity_id"], expected_id, f"Failed for alias: {query}")
            self.assertEqual(res["confidence_level"], "EXACT")

    def test_slug_resolutions(self):
        # Exact slugs
        test_cases = [
            ("whatsapp-marketing", "whatsapp_marketing"),
            ("influencer-marketing", "influencer_marketing"),
            ("ecommerce-os", "ecommerce_os"),
            ("real-estate-os", "real_estate_os")
        ]
        for query, expected_id in test_cases:
            res = core_resolver.resolve(query)
            self.assertEqual(res["entity_id"], expected_id, f"Failed for slug: {query}")
            self.assertEqual(res["confidence_level"], "EXACT")

    def test_keyword_resolutions(self):
        # Primary & secondary keywords
        test_cases = [
            ("whatsapp template", "whatsapp_marketing"),
            ("creator campaign", "influencer_marketing"),
            ("checkout optimization", "ecommerce_os"),
            ("prescription refill", "pharma_os")
        ]
        for query, expected_id in test_cases:
            res = core_resolver.resolve(query)
            self.assertEqual(res["entity_id"], expected_id, f"Failed for keyword: {query}")
            self.assertTrue(res["confidence_level"] in ("EXACT", "HIGH", "MEDIUM"))

    def test_substring_word_boundary_lookups(self):
        # Substring/phrase resolution (e.g. embedded in query text)
        res = core_resolver.resolve("tell me more about ecommerce os and checkout")
        self.assertEqual(res["entity_id"], "ecommerce_os")
        
        res = core_resolver.resolve("what is whatsapp marketing platform?")
        self.assertEqual(res["entity_id"], "whatsapp_marketing")

    def test_fuzzy_matching_rapid_fuzz(self):
        # Test fuzzy queries (WRatio >= 90%)
        test_cases = [
            ("whatsap marketing", "whatsapp_marketing"),
            ("infleucer marketing", "influencer_marketing"),
            ("ecomerce os", "ecommerce_os")
        ]
        for query, expected_id in test_cases:
            res = core_resolver.resolve(query)
            self.assertEqual(res["entity_id"], expected_id, f"Failed fuzzy match: {query}")
            self.assertEqual(res["confidence_level"], "FUZZY")

    def test_precedence_order(self):
        # Test resolution precedence:
        # ID > Alias > Slug > Keyword > Synonym > Fuzzy
        
        # Exact alias vs keyword -> Alias has precedence.
        # "e-commerce os" is an alias of ecommerce_os.
        res = core_resolver.resolve("e-commerce os")
        self.assertEqual(res["entity_id"], "ecommerce_os")
        self.assertEqual(res["confidence_level"], "EXACT")

    def test_registry_lookup_inheritance(self):
        # Resolve registry directly from entity belongs_to
        res_entity = "whatsapp_marketing"
        reg_type, score = resolve_registry(
            query="tell me about whatsapp",
            resolved_entity_id=res_entity,
            registry_index=self.registry.registry_index,
            knowledge_graph=self.registry.knowledge_graph,
            disabled_registries=set()
        )
        self.assertEqual(reg_type, "PRODUCTS")
        self.assertEqual(score, 1.0)

    def test_registry_lightweight_keywords(self):
        # Fallback keyword checks when no entity is resolved
        test_cases = [
            ("what solutions do you offer", "SOLUTIONS"),
            ("list your services", "SERVICES"),
            ("who is in your leadership team", "LEADERSHIP")
        ]
        for query, expected_reg in test_cases:
            reg_type, score = resolve_registry(
                query=query,
                resolved_entity_id=None,
                registry_index=self.registry.registry_index,
                knowledge_graph=self.registry.knowledge_graph,
                disabled_registries=set()
            )
            self.assertEqual(reg_type, expected_reg)
            self.assertEqual(score, 0.90)

    def test_negative_resolutions(self):
        # Queries that should not resolve to any entity or registry
        unresolved_queries = [
            "hello",
            "nice to meet you",
            "what is the weather in Paris",
            "who built the pyramids"
        ]
        for query in unresolved_queries:
            res = core_resolver.resolve(query)
            self.assertIsNone(res["entity_id"])
            self.assertEqual(res["confidence_level"], "NONE")

if __name__ == "__main__":
    unittest.main()
