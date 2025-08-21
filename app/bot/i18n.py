"""
Internationalization system for Karma System bot.
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class I18n:
    """Internationalization manager."""
    
    def __init__(self, locales_dir: str = "app/i18n"):
        self.locales_dir = Path(locales_dir)
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.default_locale = "ru"
        self.supported_locales = ["ru", "en", "vi", "ko"]
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files."""
        for locale in self.supported_locales:
            locale_file = self.locales_dir / f"{locale}.json"
            if locale_file.exists():
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.translations[locale] = json.load(f)
            else:
                self.translations[locale] = {}
    
    def get(self, key: str, locale: str = None, **kwargs) -> str:
        """Get translated text by key."""
        if locale is None:
            locale = self.default_locale
        
        if locale not in self.supported_locales:
            locale = self.default_locale
        
        # Navigate nested keys (e.g., "categories.restaurants")
        keys = key.split('.')
        value = self.translations.get(locale, {})
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Fallback to default locale
                value = self.translations.get(self.default_locale, {})
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return f"[{key}]"  # Missing translation
                break
        
        if isinstance(value, str):
            # Format with kwargs if provided
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value
        
        return f"[{key}]"
    
    def get_language_name(self, locale: str) -> str:
        """Get language name in its own language."""
        return self.get("languages." + locale, locale)
    
    def is_supported(self, locale: str) -> bool:
        """Check if locale is supported."""
        return locale in self.supported_locales

# Global i18n instance
i18n = I18n()

def _(key: str, locale: str = None, **kwargs) -> str:
    """Shortcut function for translations."""
    return i18n.get(key, locale, **kwargs)
