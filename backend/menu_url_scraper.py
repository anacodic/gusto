"""
Compatibility alias for menu_url_scraper.
Redirects to integrations.menu_scraper for backward compatibility with db_scripts.
"""
from integrations.menu_scraper import MenuURLScraper

__all__ = ['MenuURLScraper']
