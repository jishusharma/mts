param([string]$Json)
# Draws the primitive lists written by g3_pack.py (rect / line / text) to PNG files through GDI+.
Add-Type -AssemblyName System.Drawing
$jobs = Get-Content -Raw -Encoding UTF8 -Path $Json | ConvertFrom-Json
$fmt = [System.Drawing.Imaging.ImageFormat]::Png
foreach ($j in $jobs) {
    $bmp = New-Object System.Drawing.Bitmap ([int]$j.w), ([int]$j.h)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = 'AntiAlias'
    $g.TextRenderingHint = 'AntiAliasGridFit'
    $brushes = @{}; $pens = @{}; $fonts = @{}
    foreach ($p in $j.prims) {
        if ($p.k -eq 'rect') {
            if (-not $brushes.ContainsKey($p.c)) { $brushes[$p.c] = New-Object System.Drawing.SolidBrush ([System.Drawing.ColorTranslator]::FromHtml($p.c)) }
            $g.FillRectangle($brushes[$p.c], [single]$p.x, [single]$p.y, [single]$p.w, [single]$p.h)
        } elseif ($p.k -eq 'line') {
            $key = "$($p.c)|$($p.w)"
            if (-not $pens.ContainsKey($key)) { $pens[$key] = New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml($p.c)), ([single]$p.w) }
            $pts = New-Object 'System.Drawing.PointF[]' $p.pts.Count
            for ($i = 0; $i -lt $p.pts.Count; $i++) { $pts[$i] = New-Object System.Drawing.PointF ([single]$p.pts[$i][0]), ([single]$p.pts[$i][1]) }
            $g.DrawLines($pens[$key], $pts)
        } elseif ($p.k -eq 'text') {
            if (-not $brushes.ContainsKey($p.c)) { $brushes[$p.c] = New-Object System.Drawing.SolidBrush ([System.Drawing.ColorTranslator]::FromHtml($p.c)) }
            $fk = [string]$p.size
            if (-not $fonts.ContainsKey($fk)) { $fonts[$fk] = New-Object System.Drawing.Font 'Consolas', ([single]$p.size), ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel) }
            $g.DrawString([string]$p.s, $fonts[$fk], $brushes[$p.c], [single]$p.x, [single]$p.y)
        }
    }
    $bmp.Save([string]$j.out, $fmt)
    $g.Dispose(); $bmp.Dispose()
}
