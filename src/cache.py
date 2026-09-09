import json
from datetime import datetime, timezone
from pathlib import Path


CACHE_DIR = Path("cache")


def _cache_filename(company):
    """
    Convert a company name into a safe cache filename.

    Example:
    Datacom, Australia
    ->
    cache/datacom_australia.json
    """

    filename = company.lower()

    safe_characters = []

    for character in filename:
        if character.isalnum():
            safe_characters.append(character)
        else:
            safe_characters.append("_")

    filename = "".join(safe_characters)

    while "__" in filename:
        filename = filename.replace("__", "_")

    filename = filename.strip("_")

    return CACHE_DIR / f"{filename}.json"


def cache_exists(company):
    """
    Check whether cached research exists.
    """

    cache_file = _cache_filename(company)

    return cache_file.exists()


def load_cached_research(company):
    """
    Load research from the local cache.

    The function returns only the original research object,
    not the cache metadata.
    """

    cache_file = _cache_filename(company)

    if not cache_file.exists():
        return None

    with open(
        cache_file,
        "r",
        encoding="utf-8"
    ) as file:

        cached_data = json.load(file)

    # New cache format
    if (
        isinstance(cached_data, dict)
        and "research" in cached_data
    ):
        return cached_data["research"]

    # Backwards compatibility:
    # If an older cache file contains raw research directly,
    # still allow the engine to read it.
    return cached_data


def load_cache_metadata(company):
    """
    Return metadata about a cached research result.

    Returns None if no cache exists.
    """

    cache_file = _cache_filename(company)

    if not cache_file.exists():
        return None

    with open(
        cache_file,
        "r",
        encoding="utf-8"
    ) as file:

        cached_data = json.load(file)

    if (
        isinstance(cached_data, dict)
        and "metadata" in cached_data
    ):
        return cached_data["metadata"]

    return None


def save_research(
    company,
    research,
    model="gpt-5.6-luna"
):
    """
    Save research together with metadata.

    This gives us an audit trail showing when the
    account was researched and which model produced it.
    """

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    cache_file = _cache_filename(company)

    metadata = {
        "company": company,
        "cached_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "model": model,
        "status": "complete",
    }

    cached_data = {
        "metadata": metadata,
        "research": research,
    }

    with open(
        cache_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            cached_data,
            file,
            indent=2,
            ensure_ascii=False
        )

    return cache_file


def clear_cache():
    """
    Delete all cached research files.
    """

    if not CACHE_DIR.exists():
        return

    for cache_file in CACHE_DIR.glob("*.json"):
        cache_file.unlink()


if __name__ == "__main__":

    print("Cache module ready.")
    print(
        f"Cache directory: {CACHE_DIR}"
    )