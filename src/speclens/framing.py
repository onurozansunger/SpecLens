"""Detect a complete JSON object during streaming; never repair incomplete JSON."""

import json


def complete_json_object(text: str) -> str | None:
    if not text.lstrip().startswith("{"):
        return None
    in_string, escaped, depth = False, False, 0
    for i, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = text[: i + 1]
                try:
                    value = json.loads(candidate)
                except ValueError:
                    return None
                return candidate if isinstance(value, dict) else None
    return None
