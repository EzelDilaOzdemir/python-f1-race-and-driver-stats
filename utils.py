"""This file contains  mathematical foundation and data-cleaning utilities."""
import math

def safe_int(value, default=0):
    """Safely convert value to int, handling MySQL NULLs."""
    if value is None: return default
    try: return int(value)
    except (ValueError, TypeError): return default

def safe_float(value, default=0.0):
    """Safely convert value to float."""
    if value is None: return default
    try: return float(value)
    except (ValueError, TypeError): return default

def is_null(value):
    """Check for missing data sentinels."""
    return value is None or (isinstance(value, str) and value.strip() in ("", r"\N"))

def normalize_vector(vec):
    """Scale list to unit length (L2 normalization)."""
    mag = math.sqrt(sum(x ** 2 for x in vec))
    return [x / mag for x in vec] if mag > 0 else vec[:]

def euclidean_distance(vec_a, vec_b):
    """Pythagorean distance in N-dimensions."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))

def cosine_similarity(vec_a, vec_b):
    """Measure the angle between two vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a ** 2 for a in vec_a))
    mag_b = math.sqrt(sum(b ** 2 for b in vec_b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0