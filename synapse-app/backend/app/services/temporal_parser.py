"""
Temporal Query Parser
Parse time-based queries like "last week", "yesterday", "this month"
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
import re


class TemporalParser:
    """
    Parse natural language temporal expressions

    Examples:
    - "python async last week" → filter to last 7 days
    - "article from yesterday" → filter to yesterday
    - "captures this month" → filter to current month
    """

    def __init__(self):
        # Define temporal patterns
        self.patterns = {
            # Relative days
            r'\b(yesterday|last\s+day)\b': lambda: self._days_ago(1),
            r'\btoday\b': lambda: self._days_ago(0),
            r'\blast\s+week\b': lambda: self._days_ago(7),
            r'\blast\s+month\b': lambda: self._days_ago(30),
            r'\blast\s+year\b': lambda: self._days_ago(365),

            # This period
            r'\bthis\s+week\b': lambda: self._this_week(),
            r'\bthis\s+month\b': lambda: self._this_month(),
            r'\bthis\s+year\b': lambda: self._this_year(),

            # Last N days
            r'\blast\s+(\d+)\s+days?\b': lambda match: self._days_ago(int(match.group(1))),
            r'\blast\s+(\d+)\s+weeks?\b': lambda match: self._days_ago(int(match.group(1)) * 7),
            r'\blast\s+(\d+)\s+months?\b': lambda match: self._days_ago(int(match.group(1)) * 30),

            # Recent
            r'\b(recent|recently|latest)\b': lambda: self._days_ago(7),
        }

    def parse(self, query: str) -> Dict:
        """
        Parse query and extract temporal filter

        Args:
            query: Search query (e.g., "python async last week")

        Returns:
            {
                "cleaned_query": "python async",  # Query without temporal terms
                "start_date": datetime or None,
                "end_date": datetime or None
            }
        """
        query_lower = query.lower()

        for pattern, date_func in self.patterns.items():
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                # Get date range
                try:
                    if callable(date_func):
                        # Check if function expects match object
                        import inspect
                        sig = inspect.signature(date_func)
                        if len(sig.parameters) > 0:
                            date_range = date_func(match)
                        else:
                            date_range = date_func()
                    else:
                        date_range = date_func

                    # Remove temporal expression from query
                    cleaned_query = re.sub(pattern, '', query, flags=re.IGNORECASE).strip()
                    # Clean up extra spaces
                    cleaned_query = re.sub(r'\s+', ' ', cleaned_query)

                    return {
                        "cleaned_query": cleaned_query,
                        "start_date": date_range["start"],
                        "end_date": date_range["end"]
                    }
                except Exception as e:
                    print(f"[Temporal] Error parsing date: {e}")
                    continue

        # No temporal expression found
        return {
            "cleaned_query": query,
            "start_date": None,
            "end_date": None
        }

    def _days_ago(self, days: int) -> Dict:
        """Get date range for N days ago"""
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        return {"start": start, "end": end}

    def _this_week(self) -> Dict:
        """Get date range for current week (Monday to Sunday)"""
        today = datetime.utcnow()
        start = today - timedelta(days=today.weekday())  # Monday
        end = today
        return {"start": start.replace(hour=0, minute=0, second=0, microsecond=0), "end": end}

    def _this_month(self) -> Dict:
        """Get date range for current month"""
        today = datetime.utcnow()
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = today
        return {"start": start, "end": end}

    def _this_year(self) -> Dict:
        """Get date range for current year"""
        today = datetime.utcnow()
        start = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = today
        return {"start": start, "end": end}


# Singleton
_temporal_parser = None

def get_temporal_parser() -> TemporalParser:
    """Get or create temporal parser singleton"""
    global _temporal_parser
    if _temporal_parser is None:
        _temporal_parser = TemporalParser()
    return _temporal_parser
