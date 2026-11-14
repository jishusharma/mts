"""CBP task contract: UTC triggers, retry, one writer, fail-closed installation."""
from datetime import timedelta
from pathlib import Path
import sys
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cbp_schedule as schedule


def test_schedule_contract():
    xml = schedule.task_xml('F:/Python/python.exe', 'F:/MTS checkout/scripts/dev/cbp_schedule.py', 'F:/CBP data', utcoffset=timedelta(0))
    root = ET.fromstring(xml)
    ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
    assert [n.text for n in root.findall('.//t:StartBoundary', ns)] == [
        '2026-10-26T05:00:00Z', '2026-10-26T20:00:00Z', '2026-10-26T05:30:00Z', '2026-10-26T16:30:00Z']
    weeks = [[d.tag.split('}')[1] for d in n] for n in root.findall('.//t:DaysOfWeek', ns)]
    assert weeks == [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']] * 2 + [['Saturday'], ['Sunday']]
    schedule.validate_task_xml(xml)
    assert root.find('.//t:MultipleInstancesPolicy', ns).text == 'IgnoreNew'
    assert root.find('.//t:StartWhenAvailable', ns).text == 'true'
    assert root.find('.//t:RestartOnFailure/t:Count', ns).text == '3'
    assert 'run --home "F:/CBP data"' in root.find('.//t:Arguments', ns).text


def test_days_follow_the_host_timezone():
    ist = schedule.task_xml('p', 's', 'h', utcoffset=timedelta(hours=5, minutes=30))
    ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
    days = [[d.tag.split('}')[1] for d in n] for n in ET.fromstring(ist).findall('.//t:DaysOfWeek', ns)]
    assert days[0] == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']       # 05:00 UTC = 10:30 IST, same day
    assert days[1] == ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']     # 20:00 UTC = 01:30 IST, next day
    assert days[2:] == [['Saturday'], ['Sunday']]                                    # 05:30 / 16:30 UTC stay on the day
    utc = schedule.task_xml('p', 's', 'h', utcoffset=timedelta(0))
    assert [[d.tag.split('}')[1] for d in n] for n in ET.fromstring(utc).findall('.//t:DaysOfWeek', ns)][1] == [
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']



def test_missing_data_never_registers_or_runs(tmp_path):
    with patch.object(schedule.subprocess, 'run') as run:
        assert schedule.main(['install', '--home', str(tmp_path)]) == 1
        run.assert_not_called()


def test_scheduled_run_uses_same_store_and_propagates_error(tmp_path):
    with patch.object(schedule, 'preflight'), patch.object(schedule.subprocess, 'run') as run:
        run.return_value.returncode = 1
        assert schedule.main(['run', '--home', str(tmp_path)]) == 1
        args, kwargs = run.call_args
        assert args[0][-1] == '--force'  # idempotent: known videos are skipped, so any start time is safe
        assert kwargs['env']['CBP_STORE'] == str(tmp_path / 'cbp_store' / 'rows.json')
        assert kwargs['env']['CBP_TRANSCRIPTS'] == str(tmp_path / 'raw_transcripts_canonical')
        assert kwargs['env']['CBP_STAMP'] == str(tmp_path / 'cbp_store' / 'stamp.json')


def test_trigger_start_is_in_the_past_so_the_first_week_is_not_skipped():
    from datetime import date
    xml = schedule.task_xml('p', 's', 'h', utcoffset=timedelta(0))
    for n in ET.fromstring(xml).findall('.//{*}StartBoundary'):
        d = date.fromisoformat(n.text[:10])
        assert d <= date(2026, 10, 26), "a future StartBoundary left 10-31/11-01 unfired after the reinstall"


def test_task_runs_with_no_visible_window():
    xml = schedule.task_xml('F:/Python/python.exe', 's', 'h', utcoffset=timedelta(0))
    root = ET.fromstring(xml)
    ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
    assert root.find('.//t:Exec/t:Command', ns).text.lower().endswith('pythonw.exe')
    assert root.find('.//t:Settings/t:Hidden', ns).text == 'true'


def test_cbp_run_children_carry_no_window_flag():
    import subprocess
    import cbp_run
    flag = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    assert flag or sys.platform != 'win32'
    with patch.object(cbp_run.subprocess, 'run') as run:
        cbp_run._run(['x'])
        assert run.call_args.kwargs['creationflags'] == flag
    for fn in (cbp_run.fetch_new, cbp_run.llm_extract, cbp_run.rebuild_dashboard):
        assert fn.__defaults__ is not None and cbp_run._run in fn.__defaults__
