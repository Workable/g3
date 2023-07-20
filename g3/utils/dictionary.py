def without_nulls(dictionary: dict) -> dict:
    if not dictionary:
        return {}

    return {k: v for k, v in dictionary.items() if v is not None}
