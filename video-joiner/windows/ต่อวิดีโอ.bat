@echo off
chcp 65001 >nul
title Video Joiner
powershell -NoProfile -ExecutionPolicy Bypass -Command "$t=Join-Path $env:TEMP 'videojoiner-run.ps1'; $s=Get-Content -LiteralPath '%~f0' -Raw -Encoding UTF8; $m='#'+'PS'+'_START#'; [IO.File]::WriteAllText($t, $s.Substring($s.IndexOf($m)+$m.Length), (New-Object Text.UTF8Encoding $true)); & $t '%~dp0'"
echo.
pause
exit /b
#PS_START#
# ---------- ส่วน PowerShell: รันโดยไฟล์ .bat ข้างบน ----------
param([string]$Folder)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Folder = $Folder.TrimEnd('\')

$Base = Join-Path $env:LOCALAPPDATA "video-joiner"
$Code = Join-Path $Base "66luqrjh-main\video-joiner"
$Zip  = "https://github.com/wayu1689w-dev/66luqrjh/archive/refs/heads/main.zip"
$Exts = @(".mp4", ".mov", ".m4v", ".mkv", ".avi")
$Channels = @("เสือ2992", "เสือ954", "ชีวิตติดรีวิวของดี", "เจ้าเสือ")  # แก้ชื่อช่องได้ที่นี่ (ใช้เป็นชื่อโฟลเดอร์/ไฟล์)
$Handles  = @("@www.dada198", "@ok_d198", "@198da_d", "@www.wayu1989")

function Say($msg) { Write-Host $msg }
function Stop-With($msg) { Write-Host ""; Write-Host "ผิดพลาด: $msg" -ForegroundColor Red; exit 1 }
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
}
function Find-Python {
    foreach ($c in @("python", "py")) {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source -notlike "*WindowsApps*") { return $cmd.Source }
    }
    return $null
}

Say "=== ต่อวิดีโอ ==="
Say "โฟลเดอร์: $Folder"

# 1) หาคลิป (เรียงตามชื่อ: 1, 2, 10 ไม่ใช่ 1, 10, 2)
$clips = Get-ChildItem -LiteralPath $Folder -File |
    Where-Object { $Exts -contains $_.Extension.ToLower() -and $_.Name -ne "joined.mp4" } |
    Sort-Object { [regex]::Replace($_.BaseName, '\d+', { $args[0].Value.PadLeft(12, '0') }) }
if (-not $clips) { Stop-With "ไม่มีคลิปในโฟลเดอร์นี้ ให้วางคลิป (.mp4 / .mov) ไว้ที่เดียวกับไฟล์นี้ก่อน" }
Say ""
Say "เจอ $($clips.Count) คลิป จะต่อตามลำดับนี้:"
$i = 1; foreach ($c in $clips) { Say ("  {0}. {1}" -f $i, $c.Name); $i++ }

# 2) โหลดโค้ด (ครั้งแรกครั้งเดียว)
if (-not (Test-Path (Join-Path $Code "videojoiner"))) {
    Say ""
    Say "กำลังโหลดโปรแกรมต่อวิดีโอ (ครั้งแรกเท่านั้น)..."
    New-Item -ItemType Directory -Force -Path $Base | Out-Null
    $zipFile = Join-Path $Base "main.zip"
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $Zip -OutFile $zipFile -UseBasicParsing
        Expand-Archive -LiteralPath $zipFile -DestinationPath $Base -Force
    } catch { Stop-With "โหลดโปรแกรมไม่ได้ ตรวจว่าต่ออินเทอร์เน็ตอยู่ แล้วลองใหม่" }
}

# 3) ลง ffmpeg + Python ถ้ายังไม่มี (ครั้งแรกครั้งเดียว)
Refresh-Path
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue) -or -not (Find-Python)) {
    Say ""
    Say "กำลังลง ffmpeg และ Python (ครั้งแรกเท่านั้น อาจใช้หลายนาที)..."
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Code "scripts\setup.ps1")
    Refresh-Path
}
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { Stop-With "ยังหา ffmpeg ไม่เจอ ให้ปิดหน้าต่างนี้แล้วดับเบิลคลิกไฟล์อีกครั้ง ถ้ายังไม่ได้ให้รีสตาร์ทเครื่อง" }
$py = Find-Python
if (-not $py) { Stop-With "ยังหา Python ไม่เจอ ให้ปิดหน้าต่างนี้แล้วดับเบิลคลิกไฟล์อีกครั้ง ถ้ายังไม่ได้ให้รีสตาร์ทเครื่อง" }

# 4) เลือกช่อง -> ตั้งชื่อไฟล์ + โฟลเดอร์ตามช่อง
Say ""
Say "คลิปนี้สำหรับช่องไหน?"
for ($n = 0; $n -lt $Channels.Count; $n++) { Say ("  {0} = {1}  {2}" -f ($n + 1), $Channels[$n], $Handles[$n]) }
do {
    $pick = (Read-Host "พิมพ์เลข 1-$($Channels.Count) แล้วกด Enter").Trim()
} until ($pick -match '^\d+$' -and [int]$pick -ge 1 -and [int]$pick -le $Channels.Count)
$Channel = $Channels[[int]$pick - 1]
$OutDir = Join-Path $Folder $Channel
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Out = Join-Path $OutDir ("{0}_{1}.mp4" -f $Channel, (Get-Date -Format "yyyy-MM-dd_HHmm"))
Say "จะบันทึกเป็น: $Out"

# 5) ต่อวิดีโอ
Say ""
Say "กำลังต่อวิดีโอ (แนวตั้ง 1080x1920)..."
$env:PYTHONPATH = $Code
$env:PYTHONIOENCODING = "utf-8"
$args2 = @("-m", "videojoiner") + ($clips | ForEach-Object { $_.FullName }) + @("-o", $Out, "--size", "1080x1920")
& $py @args2
if ($LASTEXITCODE -ne 0) { Stop-With "ต่อวิดีโอไม่สำเร็จ ถ่ายรูปหน้าต่างนี้ส่งให้ Claude ดู" }

Say ""
Write-Host "เสร็จแล้ว! ไฟล์อยู่ที่: $Out" -ForegroundColor Green
Start-Process explorer.exe -ArgumentList "/select,`"$Out`""
