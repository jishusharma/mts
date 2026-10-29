param([string]$AlertFile)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type -ReferencedAssemblies System.Windows.Forms -TypeDefinition @"
using System; using System.Runtime.InteropServices; using System.Windows.Forms;
public class AlertForm : Form {
    protected override bool ShowWithoutActivation { get { return true; } }
    [StructLayout(LayoutKind.Sequential)] struct FLASHWINFO { public uint cbSize; public IntPtr hwnd; public uint dwFlags; public uint uCount; public uint dwTimeout; }
    [DllImport("user32.dll")] static extern bool FlashWindowEx(ref FLASHWINFO f);
    public void Flash() { FLASHWINFO f = new FLASHWINFO(); f.cbSize = (uint)Marshal.SizeOf(f); f.hwnd = this.Handle; f.dwFlags = 3 | 12; f.uCount = 10; f.dwTimeout = 0; FlashWindowEx(ref f); }
}
"@
# Hide the parent console window (the flash). Form is a separate window.
Add-Type -Name Win32 -Namespace ConHide -MemberDefinition @"
[DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
"@
try {
    $h = [ConHide.Win32]::GetConsoleWindow()
    [ConHide.Win32]::ShowWindow($h, 0) | Out-Null
} catch {}

$alert = Get-Content $AlertFile -Raw -Encoding UTF8 | ConvertFrom-Json

# One popup max per producer: close earlier windows of the same producer only.
# POPUP_PRODUCER_RX (the test extracts these lines; keep one regex per line)
# POPUP_PRODUCER_RX: ^MTS (ALERT )?#\d+
# POPUP_PRODUCER_RX: ^TAPE #\d+
# POPUP_PRODUCER_RX: ^MTS live health
$popupRx = @(Select-String -LiteralPath $PSCommandPath -Pattern '^# POPUP_PRODUCER_RX: (.+)$' |
    ForEach-Object { $_.Matches[0].Groups[1].Value })
$myRx = $popupRx | Where-Object { "$($alert.title)" -match $_ } | Select-Object -First 1
if ($myRx) {
    try {
        Get-Process powershell,pwsh -ErrorAction Stop | ForEach-Object {
            if ($_.Id -ne $PID -and $_.MainWindowTitle -match $myRx) {
                Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {}
}

$form = New-Object AlertForm
$form.Text = $alert.title
$form.Width = 600
$form.Height = 680
$form.StartPosition = "Manual"
# Cascade offset by alert number so stacked popups stay visible
$cascadeN = 0
if ($alert.title -match '#(\d+)') { $cascadeN = [int]$Matches[1] }
$cascadeIdx = $cascadeN % 6
$form.Location = New-Object System.Drawing.Point(
    (40 + $cascadeIdx * 40),
    (40 + $cascadeIdx * 40)
)
# TopMost removed - popup sits behind IDE
$form.TopMost = $false
$form.BackColor = [System.Drawing.Color]::FromArgb(20, 22, 28)
$form.ForeColor = [System.Drawing.Color]::White
$form.FormBorderStyle = "FixedToolWindow"

$lblTitle = New-Object System.Windows.Forms.Label
$lblTitle.Text = $alert.title
$lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)
$lblTitle.ForeColor = [System.Drawing.Color]::FromArgb(255, 190, 0)
$lblTitle.Location = New-Object System.Drawing.Point(15, 12)
$lblTitle.Width = 520
$lblTitle.Height = 28
$form.Controls.Add($lblTitle)

$lblBody = New-Object System.Windows.Forms.Label
$lblBody.Text = $alert.card_text
$lblBody.Font = New-Object System.Drawing.Font("Consolas", 9.5)
$lblBody.Location = New-Object System.Drawing.Point(15, 48)
$lblBody.Width = 565
$lblBody.Height = 560
$form.Controls.Add($lblBody)

$btnCopy = New-Object System.Windows.Forms.Button
$btnCopy.Text = "Copy Card"
$btnCopy.Location = New-Object System.Drawing.Point(15, 620)
$btnCopy.Width = 130
$btnCopy.Height = 30
$btnCopy.BackColor = [System.Drawing.Color]::FromArgb(40, 80, 140)
$btnCopy.ForeColor = [System.Drawing.Color]::White
$btnCopy.FlatStyle = "Flat"
$btnCopy.Add_Click({
    [System.Windows.Forms.Clipboard]::SetText($alert.card_text)
    $btnCopy.Text = "Copied"
    Start-Sleep -Milliseconds 600
    $form.Close()
})
$form.Controls.Add($btnCopy)

$btnLog = New-Object System.Windows.Forms.Button
$btnLog.Text = "Open Log"
$btnLog.Location = New-Object System.Drawing.Point(160, 620)
$btnLog.Width = 110
$btnLog.Height = 30
$btnLog.FlatStyle = "Flat"
$btnLog.Add_Click({
    Start-Process notepad.exe -ArgumentList (Join-Path $alert.repo "runtime_data\apparatus_log.txt")
})
$form.Controls.Add($btnLog)

$btnDismiss = New-Object System.Windows.Forms.Button
$btnDismiss.Text = "Dismiss"
$btnDismiss.Location = New-Object System.Drawing.Point(480, 620)
$btnDismiss.Width = 100
$btnDismiss.Height = 30
$btnDismiss.FlatStyle = "Flat"
$btnDismiss.Add_Click({ $form.Close() })
$form.Controls.Add($btnDismiss)

# Auto-close after 5 min if untouched
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 300000
$timer.Add_Tick({ $timer.Stop(); $form.Close() })
$timer.Start()

[console]::beep(900, 180)
$form.Add_Shown({ $form.Flash() })
$form.ShowDialog() | Out-Null
$form.Dispose()
