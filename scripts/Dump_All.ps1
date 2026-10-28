# Dump_All.ps1 - Generate Java + module dumps in one run
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$dumpDir = Join-Path $root "Dumps"
if (-not (Test-Path $dumpDir)) { New-Item -ItemType Directory -Path $dumpDir -Force | Out-Null }

function Write-MarkdownDump($title, $files, $outFile) {
    $stream = [System.IO.StreamWriter]::new($outFile, $false, [System.Text.Encoding]::UTF8)
    $stream.WriteLine("# $title")
    $stream.WriteLine("Generated on: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    $stream.WriteLine("")
    $totalChars = 0

    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($root.Length + 1) -replace '\\', '/'
        $ext = $file.Extension.ToLower()
        $lang = switch ($ext) {
            ".java"   { "java" }
            ".xml"    { "xml" }
            ".ps1"    { "powershell" }
            ".py"     { "python" }
            ".json"   { "json" }
            ".md"     { "markdown" }
            default   { "" }
        }

        $stream.WriteLine("## $relativePath")
        $stream.WriteLine('')
        $stream.WriteLine('```' + $lang)

        $reader = [System.IO.StreamReader]::new($file.FullName, [System.Text.Encoding]::UTF8)
        try {
            while (($line = $reader.ReadLine()) -ne $null) {
                $stream.WriteLine($line)
                $totalChars += $line.Length + 1
            }
        } finally {
            $reader.Close()
        }

        $stream.WriteLine('```')
        $stream.WriteLine('')
        $totalChars += 7
    }

    $stream.Close()
    Write-Host "$title -> $outFile ($($files.Count) files, ~$totalChars chars)"
}

# ------------------------------------------------------------
# 1. JAVA CORE
# ------------------------------------------------------------
Write-Host "Generating Java core dump..." -ForegroundColor Cyan

$javaFiles = @()
$fixedFiles = @("pom.xml", "scripts\Dump_BinanceDataFeed.ps1", "scripts\inventory_transcripts.ps1")
foreach ($f in $fixedFiles) {
    $full = Join-Path $root $f
    if (Test-Path $full) { $javaFiles += Get-Item $full }
}
$javaFiles += Get-ChildItem -Path "src\main\java\datafeed" -Filter *.java -File | Sort-Object Name

Write-MarkdownDump "Java Core Dump ? BinanceDataFeed" $javaFiles (Join-Path $dumpDir "dump_java.md")

# ------------------------------------------------------------
# 2. MODULE DUMPS
# ------------------------------------------------------------
$moduleMap = @{
    "core"       = @("system\01_AI_BEHAVIOR.md", "system\03_FILE_INDEX.md")
    "system_support" = @("system\COMPILED_DECISIONS.md")
    "runtime"    = @("mts\runtime\*")
    "conditions" = @("mts\conditions\*")
    "data"       = @("runtime_data\*")
    "tests"      = @("mts\tests\*")
    "research"   = @("mts\research\*.md")
    "cards"      = @("mts\cards\trading_card_generator.md")
    "methodology"= @("methodology\*")
    "extracts"   = @("extracts\fresh\*.md", "mts\extracts\cryptocred\extracted\*.md", "mts\extracts\the_flow_horse\extracted\*.md")
}

foreach ($mod in $moduleMap.Keys | Sort-Object) {
    Write-Host "`nGenerating $mod dump..." -ForegroundColor Cyan

    $patterns = $moduleMap[$mod]
    $files = @()
    foreach ($pattern in $patterns) {
        $fullPattern = Join-Path $root "MyTradingSys\$pattern"
        $items = Get-ChildItem -Path $fullPattern -File -ErrorAction SilentlyContinue
        foreach ($item in $items) {
            if ($item.Name -like "*.old") { continue }
            if ($item.Extension -eq ".png") { continue }
            $files += $item
        }
    }
    $files = $files | Sort-Object FullName -Unique

    if ($files.Count -gt 0) {
        $outFile = Join-Path $dumpDir "dump_${mod}.md"
        Write-MarkdownDump "Module dump: $mod" $files $outFile
    } else {
        Write-Host "No files found for module '$mod'." -ForegroundColor Yellow
    }
}

Write-Host "`nAll dumps generated in $dumpDir" -ForegroundColor Green

# Refresh BUILD_REPORT so dumps and preflight are always paired
$bcPath = Join-Path $PSScriptRoot "Build-Check.ps1"
if (Test-Path $bcPath) {
    Write-Host "`nRunning Build-Check..." -ForegroundColor Cyan
    & $bcPath
}
