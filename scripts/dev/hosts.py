"""One table of machine names (operator 2026-10-25, card machine-rename-aliases).

The desktop tower JIS-NB becomes JIS-DESKTOP and the Lenovo laptop DESKTOP-F7IU69N becomes JIS-LAPTOP (DECISION, OURS). The
real Windows rename happens later, so the repo must work under the old name, the new name and across the switch: every place
that compares or keys on a hostname goes through canonical() / same_host(), and state written under an old name (signals,
acks, owner files, branch names) keeps matching the new one. Stdlib only; never raises.
"""
import os
import socket

# canonical name -> (old aliases, noun, role)
HOSTS = {
    "JIS-DESKTOP": (("JIS-NB", "the desktop"), "the desktop", "live-tree desktop tower, F: drive, backup remote"),
    "JIS-LAPTOP": (("DESKTOP-F7IU69N", "the Lenovo laptop"), "the Lenovo laptop", "Lenovo laptop, testnet live loop"),
    "JIS-NUC": (("the NUC",), "the NUC", "NUC, queue worker, shares"),
}

_LOOKUP = {}
for _c, (_al, _n, _r) in HOSTS.items():
    for _k in (_c,) + tuple(_al):
        _LOOKUP[_k.lower()] = _c


def _key(name):
    n = str(name or "").strip().lower()
    for suf in (".lan", ".localdomain", ".local"):
        if n.endswith(suf):
            n = n[: -len(suf)]
    return n


def canonical(name):
    """Canonical (new) name of a known host or alias, case-insensitive; an unknown name is returned unchanged."""
    return _LOOKUP.get(_key(name), name)


def key(name):
    """Lower-case canonical name: the form to compare and to use as a dict key. Empty for an empty name."""
    return str(canonical(name) or "").strip().lower()


def same_host(a, b):
    return bool(a) and bool(b) and key(a) == key(b)


def aliases(name):
    """All names of one machine, canonical first, then the old ones (host names only, not the spoken nouns)."""
    c = canonical(name)
    if c not in HOSTS:
        return [name]
    return [c] + [a for a in HOSTS[c][0] if not a.startswith("the ")]


def noun(name):
    c = canonical(name)
    return HOSTS[c][1] if c in HOSTS else ""


def this_host():
    """Canonical name of this machine (env MTS_HOST wins, tests), else the OS hostname."""
    return canonical(os.environ.get("MTS_HOST") or socket.gethostname())


def unc_hosts(name):
    """Share host names to try, new name first, old one as fallback: unc_hosts('JIS-NB') -> ['JIS-DESKTOP', 'JIS-NB']."""
    return aliases(name)


def unc_path(host, share, *parts):
    """First existing UNC path to share on host, over the aliases of host (new name first); else the new-name path."""
    cands = [("\\\\" + h + "\\" + share).rstrip("\\") for h in unc_hosts(host)]
    for c in cands:
        try:
            if os.path.isdir(c):
                return os.path.join(c, *parts) if parts else c
        except OSError:
            pass
    return os.path.join(cands[0], *parts) if parts else cands[0]
