"""Create portable evidence, printable report and cloud ZIP; no strategy changes."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
SOURCES={
'E01':['MyTradingSys/backtest/layers/rsi/rsi_core.py','MyTradingSys/backtest/layers/FORMULAS.md'],
'E02':['MyTradingSys/backtest/layers/rsi/params/default.json','MyTradingSys/backtest/layers/rsi/rsi_events.py'],
'E03':['MyTradingSys/research/non_core_layer_audit_2026-10-12/reproductions.json','MyTradingSys/research/non_core_layer_audit_2026-10-12/test_results.json'],
'E04':['MyTradingSys/backtest/layers/alerts/live_layers.py'],
'E05':['MyTradingSys/execution/auto_trader.py','MyTradingSys/execution/auto_trader_config.json'],
'E06':['MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md'],
'E07':['MyTradingSys/backtest/layers/rsi/malkan_40_60.py','MyTradingSys/backtest/layers/rsi/malkan_mtf.py'],
'E08':['MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py'],
'E09':['MyTradingSys/research/rsi_kurisko_2026-10-09/RSI_HISTORY.md','MyTradingSys/research/MARKET_GUIDE_RESULTS_2026-10-07.md'],
'E10':['extracts/processed/malkan/extract_Wvq1TZh8aF0.md','extracts/processed/malkan/extract_cQ-y1oULkBw.md','extracts/processed/malkan/extract_-CBvFi40sIQ.md','extracts/processed/malkan/extract_2HcJ3NeZmEQ.md'],
'E11':['MyTradingSys/backtest/layers/rsi/rsi_divergence.py'],
'E12':['MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py','MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md'],
'E13':['MyTradingSys/backtest/layers/rsi/rsi_reclaim.py','MyTradingSys/research/rsi_2a_2026-10-09/RSI_2A_SPEC.md'],
'E14':['MyTradingSys/research/t090_7h_2026-10-09/RESULT.md'],
'E15':['MyTradingSys/items/T061_wavetrend_lazybear.md'],
'E16':['MyTradingSys/research/T065_LAZYBEAR_SURVEY.md','MyTradingSys/items/T065_lazybear_survey.md'],
'E17':['MyTradingSys/backtest/layers/cryptocred/cc_setups.py','MyTradingSys/backtest/layers/cryptocred/cc_bt_adapter.py'],
'E18':['extracts/processed/cryptocred/extract_BHwoN7VPrBE.md','MyTradingSys/research/no_source_sweep_2026-10-09/RESULT.md'],
'E19':['MyTradingSys/research/AUDIT_CLOSEOUT_2026-10-07.md','MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md'],
'E20':['MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md'],
'E21':['MyTradingSys/backtest/layers/session/session_momentum.py','MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py','MyTradingSys/backtest/layers/alerts/live_runner_cli.py'],
'E22':['MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md'],
'E23':['MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md'],
'E24':['MyTradingSys/backtest/layers/tick/build_tiers.py','MyTradingSys/backtest/layers/tick/tiers_meta.json','MyTradingSys/backtest/layers/tick/tick_flagger.py'],
'E25':['MyTradingSys/backtest/layers/timeframe/tf_resample.py','MyTradingSys/backtest/layers/timeframe/registry.json'],
'E26':['MyTradingSys/backtest/layers/consensus/hook.py','MyTradingSys/backtest/layers/consensus/README.md','MyTradingSys/backtest/layers/rsi/observation.py'],
'E27':['MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md','MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md'],
'E28':['MyTradingSys/research/b154_stratified_2026-10-09/RESULT.md'],
'E29':['MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md'],
'E30':['MyTradingSys/backtest/PRE_REG_TEMPLATE.md','MyTradingSys/PROJECT_VISION.md','MyTradingSys/system/control_room.json'],
}

def evidence():
    lines=['# Evidence attachment - independent layer audit','',
           'Captured source files with exact line numbers and SHA-256 hashes of original bytes. Trailing whitespace is omitted from displayed lines. Historical documents are evidence of what was reported, not fresh market-data reproductions. Full source snapshots below allow cloud review without local file access.','']
    manifest={}
    for key,paths in SOURCES.items():
        lines += ['## '+key,'']
        for rel in paths:
            raw=(ROOT/rel).read_bytes()
            digest=hashlib.sha256(raw).hexdigest()
            content=raw.decode('utf-8-sig')
            manifest[rel]={'sha256':digest,'bytes':len(raw),'lines':len(content.splitlines())}
            lines += ['### '+rel,'','SHA-256: `'+digest+'`','', '```text']
            lines += [f'{i}: {line}'.rstrip() for i,line in enumerate(content.splitlines(),1)]
            lines += ['```','']
    (OUT/'EVIDENCE.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    (OUT/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')

def pdf():
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4,landscape
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyAudit',fontName='Helvetica',fontSize=9.2,leading=13,spaceAfter=7))
    styles.add(ParagraphStyle(name='CellAudit',fontName='Helvetica',fontSize=8,leading=10.5,spaceAfter=3))
    styles['Heading1'].fontSize=21
    styles['Heading1'].leading=25
    styles['Heading2'].fontSize=14
    styles['Heading2'].leading=18
    styles['Heading2'].spaceBefore=15
    styles['Heading3'].fontSize=11
    def fmt(s):
        s=escape(s)
        s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
        s=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s)
        return s
    flow=[]
    md=(OUT/'REPORT.md').read_text(encoding='utf-8').splitlines()
    i=0
    width=landscape(A4)[0]-80
    while i<len(md):
        line=md[i].strip()
        if not line: i+=1; continue
        if line.startswith('|'):
            rows=[]
            while i<len(md) and md[i].strip().startswith('|'):
                cells=[x.strip() for x in md[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',x) for x in cells):
                    rows.append([Paragraph(fmt(x),styles['CellAudit']) for x in cells])
                i+=1
            n=len(rows[0])
            weights={5:[.15,.22,.25,.14,.24],4:[.20,.28,.26,.26]}.get(n,[1/n]*n)
            table=Table(rows,colWidths=[width*w for w in weights],repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce7ef')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#bfcbd5')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f8fa')])]))
            flow.extend([table,Spacer(1,9)])
            continue
        heading=re.match(r'^(#{1,3}) (.+)',line)
        if heading:
            flow.append(Paragraph(fmt(heading[2]),styles['Heading'+str(len(heading[1]))]))
        else:
            flow.append(Paragraph(fmt(line),styles['BodyAudit']))
        i+=1
    target=OUT/'NON_CORE_LAYER_AUDIT.pdf'
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(colors.HexColor('#526778'))
        canvas.drawString(40,23,'MTS | Independent layer audit | 12 October 2026 | Evidence attachment supplied separately')
        canvas.drawRightString(landscape(A4)[0]-40,23,str(doc.page))
    SimpleDocTemplate(str(target),pagesize=landscape(A4),rightMargin=40,leftMargin=40,topMargin=32,bottomMargin=38,title='MTS Independent Layer Audit',author='MTS research').build(flow,onFirstPage=footer,onLaterPages=footer)
    print(target)

def package():
    dest=OUT/'MTS_LAYER_AUDIT_CLOUD.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            if p.suffix in ('.md','.json','.txt','.py','.pdf'):
                z.write(p,p.name)
        for name in ['summary.json','summary_T088.json','REPORT.md','REPORT_T088.md']:
            p=ROOT/'MyTradingSys/research/rsi_divergence_mtf_2026-10-09'/name
            z.write(p,'original_divergence_results/'+name)
    print(dest, dest.stat().st_size)

if __name__=='__main__':
    evidence()
    pdf()
    package()
