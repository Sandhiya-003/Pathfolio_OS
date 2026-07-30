from typing import Dict, List

CATEGORY_EMOJIS = {
    "certification": "📜",
    "project": "🚀",
    "internship": "💼",
    "achievement": "🏆",
    "academic": "🎓",
    "resume": "📄",
    "portfolio": "🖼️",
    "other": "📁"
}

CATEGORY_COLORS = {
    "certification": "#10b981",
    "project": "#3b82f6",
    "internship": "#8b5cf6",
    "achievement": "#f59e0b",
    "academic": "#06b6d4",
    "resume": "#64748b",
    "portfolio": "#ec4899",
    "other": "#6b7280"
}

def get_category_emoji(category: str) -> str:
    """Get emoji for category"""
    return CATEGORY_EMOJIS.get(category.lower(), "📁")

def get_category_color(category: str) -> str:
    """Get color for category"""
    return CATEGORY_COLORS.get(category.lower(), "#6b7280")

def get_all_categories() -> List[str]:
    """Get list of all categories"""
    return list(CATEGORY_EMOJIS.keys())