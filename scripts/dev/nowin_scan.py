"""Find subprocess calls without creationflags (hidden-console rule; test_nowin_calls.py). Pure AST, no imports of the scanned code."""
import ast

FN = {"run", "Popen", "check_output", "call", "check_call"}


def offending_calls(src):
    """Each subprocess run/Popen/check_output/call/check_call without a creationflags keyword (or ** spread): dict with lineno, end_lineno,
    end_col (utf-8 offset after the closing paren), captured (output is not the console, so CREATE_NO_WINDOW is safe)."""
    tree = ast.parse(src)
    names = {a.asname or a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module == "subprocess"
             for a in n.names if a.name in FN}
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        is_attr = isinstance(f, ast.Attribute) and f.attr in FN and isinstance(f.value, ast.Name) and f.value.id == "subprocess"
        is_name = isinstance(f, ast.Name) and f.id in names
        if not (is_attr or is_name):
            continue
        kws = {k.arg for k in n.keywords}
        if "creationflags" in kws or None in kws:
            continue
        name = f.attr if is_attr else f.id
        cap = bool(kws & {"capture_output", "stdout", "stderr"}) or name == "check_output"
        out.append({"lineno": n.lineno, "end_lineno": n.end_lineno, "end_col": n.end_col_offset, "captured": cap, "name": name,
                    "from_import": is_name})
    return out
