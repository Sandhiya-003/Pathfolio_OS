from datetime import datetime
from typing import Optional
import re

def parse_date(date_str: str) -> Optional[str]:
    """Parse various date formats to YYYY-MM-DD"""
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%d %B %Y",
        "%Y"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # Try to extract just year
    year_match = re.search(r'\b(20\d{2})\b', date_str)
    if year_match:
        return f"{year_match.group(1)}-01-01"
    
    return None

def get_current_year() -> int:
    """Get current year"""
    return datetime.now().year

def format_year_range(start_year: int, end_year: int = None) -> str:
    """Format year range"""
    if end_year is None:
        end_year = get_current_year()
    return f"{start_year} - {end_year}"