# -*- coding: utf-8 -*-
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, List, Optional

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
}


@dataclass
class ScrapeContext:
    from_date: str
    to_date: str
    max_pages: int = 50
    delay_seconds: float = 2.0
    retries: int = 3
    log: Optional[Callable[[str], None]] = None

    def say(self, msg: str) -> None:
        if self.log:
            self.log(msg)
        else:
            print(msg, flush=True)


def fetch_html(session: requests.Session, url: str, ctx: ScrapeContext) -> str:
    last_error = None
    for attempt in range(1, ctx.retries + 1):
        try:
            ctx.say(f"GET {url} attempt {attempt}/{ctx.retries}")
            r = session.get(url, timeout=45)
            ctx.say(f"HTTP {r.status_code}, {len(r.text or '')} chars")
            if r.status_code == 200 and r.text:
                return r.text
            last_error = RuntimeError(f"HTTP {r.status_code}")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            ctx.say(f"ERROR {repr(exc)}")
        time.sleep(ctx.delay_seconds * attempt + random.uniform(0.2, 1.2))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def soup_text(html: str) -> str:
    return BeautifulSoup(html, "lxml").get_text(" ", strip=True)


def new_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    return session
