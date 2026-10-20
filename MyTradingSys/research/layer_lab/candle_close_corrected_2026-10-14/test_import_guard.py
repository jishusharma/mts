import subprocess
import sys
import unittest
from pathlib import Path


class ImportGuardTests(unittest.TestCase):
    def test_broken_application_import_is_not_dependency_skip(self):
        folder=Path(__file__).resolve().parent.parent/'candle_close_2026-10-14'
        code="""import builtins,runpy,types
original=builtins.__import__
def hook(name,*args,**kwargs):
    if name=='pandas': return types.ModuleType('pandas')
    if name=='study': raise ImportError('EXPECTED: broken application import')
    return original(name,*args,**kwargs)
builtins.__import__=hook
runpy.run_path('test_study.py',run_name='__main__')
"""
        r=subprocess.run([sys.executable,'-c',code],cwd=folder,capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertIn('broken application import',r.stderr)


if __name__=='__main__': unittest.main()
