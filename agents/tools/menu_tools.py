"""
Menu scraping tools for agent system.
Uses the exact same MenuURLScraper from swaad/backend/menu_url_scraper.py
"""
import json
import sys
import os
from typing import List

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import MenuURLScraper from swaad (via gusto integrations which match swaad exactly)
from integrations.menu_scraper import MenuURLScraper
from strands import tool

# Global scraper instance
_menu_scraper = None


def get_menu_scraper() -> MenuURLScraper:
    """Get or initialize MenuURLScraper instance."""
    global _menu_scraper
    if _menu_scraper is None:
        try:
            _menu_scraper = MenuURLScraper()
        except Exception as e:
            print(f"❌ [Menu Scraper] Failed to initialize: {e}")
    return _menu_scraper


@tool
def scrape_menu_url_tool(menu_url: str) -> str:
    """Scrape dishes from a restaurant menu URL.
    
    Uses the same MenuURLScraper.scrape_menu_url() function from swaad.
    Supports HTML, PDF, and image menus.
    
    Args:
        menu_url: URL to the restaurant's menu (HTML/PDF/Image)
    
    Returns:
        JSON string with list of dish names
    """
    print(f"🍽️ [Menu Scraper] Scraping menu: {menu_url}")
    
    try:
        scraper = get_menu_scraper()
        if scraper is None:
            print("❌ [Menu Scraper] Menu scraper not available")
            return json.dumps({"error": "Menu scraper not initialized", "dishes": []})
        
        dishes = scraper.scrape_menu_url(menu_url)
        
        print(f"✅ [Menu Scraper] Extracted {len(dishes)} dishes")
        
        return json.dumps({
            "dishes": dishes,
            "count": len(dishes),
            "menu_url": menu_url
        }, indent=2)
        
    except Exception as e:
        print(f"❌ [Menu Scraper] Error: {str(e)}")
        return json.dumps({
            "error": str(e),
            "dishes": [],
            "count": 0,
            "menu_url": menu_url
        })
