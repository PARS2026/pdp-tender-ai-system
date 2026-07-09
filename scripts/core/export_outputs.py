# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
from typing import Dict, List

import pandas as pd


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_json(path: str, payload: Dict) -> None:
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_tabular(prefix: str, rows: List[Dict]) -> None:
    ensure_dir(os.path.dirname(prefix) or ".")
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame([{"message": "NO DATA"}])
    df.to_csv(prefix + ".csv", index=False, encoding="utf-8-sig")
    df.to_excel(prefix + ".xlsx", index=False)
