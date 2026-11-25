# ตรวจและติดตั้ง ffmpeg + Python บน Windows (ใช้ winget)
# Claude จะรันสคริปต์นี้ให้เมื่อผู้ใช้อนุญาต: powershell -ExecutionPolicy Bypass -File setup.ps1
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
}

function Find-Python {
    foreach ($c in @("python", "py")) {
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        # ข้าม python ปลอมของ Microsoft Store (WindowsApps) ที่แค่เปิดหน้า Store
        if ($cmd -and $cmd.Source -notlike "*WindowsApps*") { return $c }
    }
    return $null
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Output "ไม่พบ winget: เปิด Microsoft Store ค้นหา 'App Installer' แล้วติดตั้ง จากนั้นลองใหม่"
    exit 2
}

$need = @()
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { $need += "Gyan.FFmpeg" }
if (-not (Find-Python)) { $need += "Python.Python.3.12" }

foreach ($id in $need) {
    Write-Output "กำลังติดตั้ง $id ..."
    winget install --id $id -e --silent --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) { Write-Output "ติดตั้ง $id ไม่สำเร็จ (รหัส $LASTEXITCODE)"; exit 1 }
}
Refresh-Path

$ok = $true
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Output ("ffmpeg พร้อม: " + ((ffmpeg -version | Select-Object -First 1)))
} else { Write-Output "ยังไม่พบ ffmpeg: ปิดแล้วเปิด Claude Code ใหม่ หรือรีสตาร์ทเครื่อง"; $ok = $false }
$py = Find-Python
if ($py) { Write-Output ("Python พร้อม: " + (& $py --version) + " (คำสั่ง: $py)") }
else { Write-Output "ยังไม่พบ Python: ปิดแล้วเปิด Claude Code ใหม่ หรือรีสตาร์ทเครื่อง"; $ok = $false }

if ($ok) { Write-Output "พร้อมใช้งาน"; exit 0 } else { exit 3 }
