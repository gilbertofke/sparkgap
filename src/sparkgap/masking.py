"""Secret masking. Every output path must go through mask()."""


def mask(value: str) -> str:
    """Show only the first and last two characters of a secret.

    Values of eight characters or fewer are fully masked, and the mask has a
    fixed width so the output never reveals the secret's length.
    """
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return f"{value[:2]}****{value[-2:]}"
