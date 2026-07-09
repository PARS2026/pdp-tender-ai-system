# -*- coding: utf-8 -*-
"""Text/date helpers for Persian tender scraping."""
from __future__ import annotations

import re
from typing import Optional, Tuple

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
EN_DIGITS = "0123456789"
DIGIT_TRANS = str.maketrans(PERSIAN_DIGITS + ARABIC_DIGITS, EN_DIGITS * 2)


def fa_to_en_digits(value: object) -> str:
    return str(value or "").translate(DIGIT_TRANS)


def clean_text(value: object) -> str:
    text = fa_to_en_digits(value)
    text = text.replace("ي", "ی").replace("ك", "ک")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_persian(value: object) -> str:
    text = clean_text(value).lower()
    text = re.sub(r"[\u200c\u200f\u202a-\u202e]", " ", text)
    text = re.sub(r"[^0-9a-zA-Zآ-ی]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def jalali_tuple(value: object) -> Optional[Tuple[int, int, int]]:
    s = fa_to_en_digits(value)
    m = re.search(r"(1[34]\d{2})[/-](\d{1,2})[/-](\d{1,2})", s)
    if not m:
        return None
    y, mo, d = map(int, m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return None
    return y, mo, d


def jalali_canonical(value: object) -> str:
    t = jalali_tuple(value)
    if not t:
        return ""
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"


def jalali_slash(value: object) -> str:
    t = jalali_tuple(value)
    if not t:
        return ""
    return f"{t[0]:04d}/{t[1]:02d}/{t[2]:02d}"


def jalali_dash(value: object) -> str:
    t = jalali_tuple(value)
    if not t:
        return ""
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"


def in_jalali_range(value: object, from_date: str, to_date: str) -> bool:
    t = jalali_tuple(value)
    f = jalali_tuple(from_date)
    to = jalali_tuple(to_date)
    if not t or not f or not to:
        return False
    return f <= t <= to


def extract_jalali_dates(text: object) -> list[str]:
    s = fa_to_en_digits(text)
    found = re.findall(r"1[34]\d{2}[/-]\d{1,2}[/-]\d{1,2}", s)
    out = []
    for item in found:
        c = jalali_canonical(item)
        if c and c not in out:
            out.append(c)
    return out


def make_stable_key(*parts: object) -> str:
    base = " ".join(normalize_persian(p) for p in parts if p)
    base = re.sub(r"\b(page|source|url)\b", " ", base)
    return re.sub(r"\s+", " ", base).strip()[:240]
