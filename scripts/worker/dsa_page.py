import sys; sys.dont_write_bytecode = True
"""Playwright adapter for the DSA chat page (implements dsa_worker.ChatPage).

Attaches to the operator's own Chrome over CDP (start-dsa-chrome.ps1, port 9222,
127.0.0.1 only). The operator logs in by hand. This module never types
credentials, never touches a challenge page, and has no stealth or
anti-detection code: on a challenge it only reports challenge_seen() and the
worker pauses.

playwright is imported lazily so the worker tests run without it installed.
Selectors live in dsa_selectors.json (see the comments there for calibration).
"""
import json
from pathlib import Path

from dsa_worker import ChatPage, PageError

ACTION_TIMEOUT_MS = 15000


class PlaywrightChatPage(ChatPage):
    def __init__(self, cdp_url, selectors_file):
        with open(selectors_file, encoding="utf-8") as fh:
            self.sel = {k: v for k, v in json.load(fh).items() if not k.startswith("_")}
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise SystemExit("playwright is not installed: pip install playwright "
                             "(no browser download needed, it attaches to Chrome)") from exc
        self._pw = sync_playwright().start()
        try:
            self._browser = self._pw.chromium.connect_over_cdp(cdp_url)
        except Exception as exc:
            raise SystemExit(f"cannot attach to Chrome at {cdp_url}: run start-dsa-chrome.ps1 first ({exc})")
        self._ctx = self._browser.contexts[0] if self._browser.contexts else self._browser.new_context()
        try:
            self._ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        except Exception:
            pass  # fallback path (innerText) still works
        self._page = self._ctx.pages[0] if self._ctx.pages else self._ctx.new_page()

    # ---- helpers ----
    def _count(self, name):
        try:
            return self._page.locator(self.sel[name]).count()
        except Exception:
            return 0

    def _last(self, name):
        return self._page.locator(self.sel[name]).last

    # ---- ChatPage ----
    def new_chat(self):
        try:
            self._page.goto(self.sel["chat_url"], wait_until="domcontentloaded", timeout=30000)
            self._page.locator(self.sel["input"]).first.wait_for(state="visible", timeout=ACTION_TIMEOUT_MS)
        except Exception as exc:
            if self.challenge_seen():
                return  # the worker checks challenge_seen() next and pauses
            raise PageError(f"new chat failed: {exc}")

    def send(self, prompt):
        try:
            box = self._page.locator(self.sel["input"]).first
            box.click(timeout=ACTION_TIMEOUT_MS)
            box.fill(prompt, timeout=ACTION_TIMEOUT_MS)  # one paste-like insert, no key-by-key typing
            self._page.locator(self.sel["send"]).first.click(timeout=ACTION_TIMEOUT_MS)
        except Exception as exc:
            raise PageError(f"send failed: {exc}")

    def challenge_seen(self):
        # Only VISIBLE challenge elements count. A text-phrase check is
        # not used: the worker sends the spec (which may inline this very
        # selectors file) as a prompt, so the phrase list appears in the
        # page body and would always fire.
        try:
            loc = self._page.locator(self.sel["challenge"])
            n = loc.count()
            for i in range(n):
                try:
                    if loc.nth(i).is_visible():
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def is_generating(self):
        return self._count("stop") > 0

    def current_text(self):
        if not self._count("last_answer"):
            return ""
        try:
            return self._last("last_answer").inner_text(timeout=5000)
        except Exception:
            return ""

    def read_last(self):
        text = ""
        try:
            if self._count("copy_button"):
                self._last("copy_button").click(timeout=ACTION_TIMEOUT_MS)
                text = self._page.evaluate("navigator.clipboard.readText()") or ""
        except Exception:
            text = ""
        return text if text.strip() else self.current_text()

    def calibrate(self):
        """Match counts for the six selectors; challenge is excluded (0 matches is healthy)."""
        return {name: self._count(name) for name in ("input", "send", "stop", "last_answer", "copy_button")}
