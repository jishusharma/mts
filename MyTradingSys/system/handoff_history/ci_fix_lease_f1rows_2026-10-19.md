# CI fix patch (lease.role_name(None) + f1_rows lint + tests)

Extract the block below into a file and `git apply` it (it is a plain unified diff against trunk 6c9ea047).

```diff
diff --git a/MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/f1_rows.py b/MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/f1_rows.py
index 7228cf64..d275d74e 100644
--- a/MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/f1_rows.py
+++ b/MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/f1_rows.py
@@ -56,7 +56,8 @@ def main():
         print("chunk %s: %d unreviewed rows" % (args.chunk, len(rows)))
         return 0
     start, n = args.show
-    for k, a in enumerate(rows[start:start + n], start):
+    stop = start + n
+    for k, a in enumerate(rows[start:stop], start):
         f, pat, src = a[0], a[1], a[2]
         lines = (REPO / f).read_text(encoding="utf-8", errors="replace").splitlines()
         hits = [i for i, t in enumerate(lines) if norm(t) == norm(src) or norm(src) in norm(t) or norm(t) in norm(src) and len(norm(t)) > 12]
diff --git a/MyTradingSys/tests/test_lease.py b/MyTradingSys/tests/test_lease.py
index 90a60e97..5d3666a0 100644
--- a/MyTradingSys/tests/test_lease.py
+++ b/MyTradingSys/tests/test_lease.py
@@ -283,5 +283,17 @@ class Wiring(Base):
         self.assertEqual(role_loader.lease_suffix("Eagle_Eyes", self.b), "")
 
 
+class RoleNameNoRoleTest(unittest.TestCase):
+    """A roleless session (no MTS_ROLE, no injected role) made current_role() None; role_name(None) raised AttributeError
+    and crashed every `sync.py ship` (found 2026-10-19 on the Lenovo)."""
+
+    def test_none_role_does_not_raise(self):
+        self.assertIsNone(lease.role_name(None))
+
+    def test_plain_string_still_canonical(self):
+        self.assertEqual(lease.role_name("pipeliner"), "Pipeliner")
+        self.assertEqual(lease.role_name("Eagle_Eyes"), "Eagle_Eyes")
+
+
 if __name__ == "__main__":
     unittest.main()
diff --git a/scripts/dev/lease.py b/scripts/dev/lease.py
index 90c408f2..224c2ada 100644
--- a/scripts/dev/lease.py
+++ b/scripts/dev/lease.py
@@ -129,6 +129,8 @@ def home():
 # ---------- which role is this session ----------
 def role_name(role):
     """Exact singleton name for any spelling (pipeliner, traffic controller); other names unchanged, never raises."""
+    if not isinstance(role, str):
+        return role
     try:
         return canon(role)
     except LeaseError:

```
