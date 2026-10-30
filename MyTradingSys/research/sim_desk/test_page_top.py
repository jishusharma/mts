"""Simulator Desk top of page: Advanced is a collapsed container holding fees/slippage/conditions, the banner is one
line, chips never wrap, no repeated title, and R is labelled in plain words."""
import re
from pathlib import Path

PAGE = (Path(__file__).resolve().parent / 'page.html').read_text(encoding='utf-8')


def test_advanced_container_collapsed():
    m = re.search(r'<details([^>]*id="adv"[^>]*)>(.*?)</details>', PAGE, re.S)
    assert m, 'no #adv container'
    assert ' open' not in m.group(1)
    assert 'id="advform"' in m.group(2) and 'id="condfields"' in m.group(2)
    assert "'maker_pct', 'taker_pct', 'slip_pct'" in PAGE


def test_banner_one_line():
    m = re.search(r'<div class="banner"[^>]*>(.*?)</div>', PAGE, re.S)
    assert m and '\n' not in m.group(1) and len(m.group(1)) < 130
    assert re.search(r'\.banner \{[^}]*white-space:nowrap', PAGE)


def test_chips_fixed_row_and_no_repeated_title():
    assert re.search(r'\.chips \{[^}]*flex-wrap:nowrap', PAGE)
    assert "$('title')" not in PAGE


def test_plain_word_r_label():
    assert 'profit per unit risked' in PAGE


def test_extra_numbers_collapsed():
    assert re.search(r'<details class="fold"><summary>More numbers</summary><div class="nums" id="nums2">', PAGE)
