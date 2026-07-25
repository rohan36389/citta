from typing import List, Optional
from backend.presentation.config.ui_theme import UI_THEME

class SectionRenderer:
    """
    Shared utility for formatting presentation elements consistently.
    """
    
    @staticmethod
    def render_header(title: str, domain: str, tagline: Optional[str] = None) -> str:
        """
        Renders the primary header with the appropriate domain icon.
        """
        icon = UI_THEME["ICONS"].get(domain.lower(), UI_THEME["ICONS"]["default"])
        header = f"{icon} **{title}**\n\n"
        
        if tagline:
            header += f"*{tagline}*\n\n"
            
        return header

    @staticmethod
    def render_section(section_key: str, items: Optional[List[str]]) -> str:
        """
        Renders a bulleted section safely. Returns empty string if no items.
        """
        if not items:
            return ""
            
        title = UI_THEME["SECTION_TITLES"].get(section_key, section_key.replace('_', ' ').title())
        
        md = f"**{title}**\n\n"
        for item in items:
            md += f"• {item}\n"
        md += "\n"
        return md
        
    @staticmethod
    def render_actions(action_keys: Optional[List[str]]) -> str:
        """
        Renders contextual action buttons as links.
        """
        if not action_keys:
            return ""
            
        md = f"**{UI_THEME['SECTION_TITLES']['next_actions']}**\n\n"
        
        for key in action_keys:
            btn_def = UI_THEME["BUTTONS"].get(key)
            if btn_def:
                md += f"[{btn_def['label']}]({btn_def['route']})\n\n"
                
        return md
