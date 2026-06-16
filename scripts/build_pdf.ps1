$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$PaperDir = Join-Path $Root "paper"
$DownloadsPdf = "C:\Users\wangz\Downloads\56.pdf"
$LocalPdf = Join-Path $PaperDir "main.pdf"
$BuildStatus = Join-Path $Root "data\build_status.json"

Push-Location $PaperDir
try {
    pdflatex -interaction=nonstopmode -halt-on-error main.tex | Out-Null
    pdflatex -interaction=nonstopmode -halt-on-error main.tex | Out-Null
}
finally {
    Pop-Location
}

$PdfInfo = & pdfinfo $LocalPdf
$PagesLine = $PdfInfo | Select-String -Pattern "^Pages:\s+(\d+)" | Select-Object -First 1
if (-not $PagesLine) {
    throw "Could not read page count from $LocalPdf"
}
$Pages = [int]$PagesLine.Matches[0].Groups[1].Value
if ($Pages -lt 25) {
    throw "Final PDF has $Pages pages; expected at least 25 pages."
}

$LocalLength = (Get-Item -LiteralPath $LocalPdf).Length
$Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $LocalPdf).Hash

Copy-Item -LiteralPath $LocalPdf -Destination $DownloadsPdf -Force
Remove-Item -LiteralPath $LocalPdf -Force

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $BuildStatus) | Out-Null
$Status = [ordered]@{
    paper = 56
    decision = "final_v3_full_scale"
    canonical_pdf = $DownloadsPdf
    pages = $Pages
    file_size_bytes = $LocalLength
    sha256 = $Hash
    local_pdf_removed = -not (Test-Path -LiteralPath $LocalPdf)
    built_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz")
}
$Status | ConvertTo-Json | Set-Content -Path $BuildStatus -Encoding ASCII

Get-Item -LiteralPath $DownloadsPdf | Select-Object FullName,Length,LastWriteTime
Write-Host "Local paper/main.pdf exists:" (Test-Path -LiteralPath $LocalPdf)
