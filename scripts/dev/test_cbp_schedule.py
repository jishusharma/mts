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
        '2026-11-02T05:00:00Z', '2026-11-02T20:00:00Z', '2026-11-02T05:30:00Z', '2026-11-02T16:30:00Z']
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
