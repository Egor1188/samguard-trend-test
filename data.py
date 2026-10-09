"""Test data. The tags below exist in the demo plant ("Jakob Petro and Sons") on demo-3."""
import random
import string
from typing import Iterable, List

TAG_POOL = ["FI8903", "PI527", "LI3606", "TI4972", "PI3901A", "TI8325", "LC81013"]


def unique_section_name() -> str:
    """A valid name per spec 2.2: English letters and digits only, exactly 10 characters."""
    return "Auto" + "".join(random.choices(string.digits, k=6))


def pick_tags(exclude: Iterable[str], count: int) -> List[str]:
    """`count` tags from TAG_POOL that are not already in the section."""
    excluded = set(exclude)
    available = [tag for tag in TAG_POOL if tag not in excluded]
    if len(available) < count:
        raise ValueError(f"TAG_POOL has only {len(available)} free tags, {count} needed")
    return available[:count]
