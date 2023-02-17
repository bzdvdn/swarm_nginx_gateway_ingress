def parse_dotnames_to_dict(rows: dict) -> dict:
    result = {}
    for item, value in rows.items():
        current = result
        *key_parts, last_key_part = item.split('.')
        for key_part in key_parts:
            current = current.setdefault(key_part, {})
        current[last_key_part] = value
    return result
