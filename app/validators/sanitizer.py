# app/validators/sanitizer.py

import bleach
import re


def sanitize_text(text: str) -> str:
    """Видаляє ВСІ HTML-теги з тексту."""
    # bleach.clean знаходить і повністю вирізає теги (<script>, <img> тощо)
    cleaned = bleach.clean(text, tags=[], strip=True)
    return cleaned.strip()


def contains_sql_patterns(text: str) -> bool:
    """Перевіряє наявність підозрілих SQL-патернів."""
    sql_patterns = [
        r"(\b(UNION|SELECT|INSERT|DELETE|DROP)\b)",
        r"(--|;\/\*|\*\/)",
        r"(\bOR\b\s+\b1\s*=\s*1\b)",
    ]
    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False