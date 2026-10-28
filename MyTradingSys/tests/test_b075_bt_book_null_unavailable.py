"""B075 residual / B084: a null (or absent, or 0.0 no-data) book_imbalance in the Java proof block surfaces as
"UNAVAILABLE" in the math object (result["proof_book_imbalance"]), never as the 1.0 default or a number.
Expected values from the task brief (null -> UNAVAILABLE) and test_book_imbalance_nodata.py (0.0 = no order-book data).
Fails on the pre-change code: the key does not exist there.
Note: dict.get(key, 1.0) returns None for a present-but-null key; the default only fires when the key is absent."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from test_book_imbalance_nodata import _ABSENT, snap  # noqa: E402
from math_object_builder import build_math_object  # noqa: E402


def _surf(direction, book=_ABSENT):
    return build_math_object(snap(direction, book)).get("proof_book_imbalance")


def test_null_book_is_unavailable_long():
    assert _surf("long", None) == "UNAVAILABLE"


def test_null_book_is_unavailable_short():
    assert _surf("short", None) == "UNAVAILABLE"


def test_absent_book_is_unavailable_not_default_1_0():
    assert _surf("long") == "UNAVAILABLE"


def test_zero_book_is_unavailable():
    assert _surf("long", 0.0) == "UNAVAILABLE"


def test_real_book_passes_through():
    assert _surf("long", 1.07) == 1.07
