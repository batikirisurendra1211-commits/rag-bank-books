def chunk_text(
    text: str,
    chunk_size: int = 2500,
    overlap: int = 300,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text:
            Text that needs to be split.

        chunk_size:
            Maximum number of characters in each chunk.

        overlap:
            Number of characters shared between consecutive chunks.

    Returns:
        List of text chunks.
    """

    if not text:
        return []

    text = text.strip()

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length,
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks