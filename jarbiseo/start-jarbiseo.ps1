# JARBISEO one-click launcher (called by 자비서시작.bat)
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
Set-Location -Path $PSScriptRoot

function Wait-Exit($code) {
    Write-Host ''
    Read-Host '  창을 닫으려면 Enter 키를 눌러 주세요'
    exit $code
}

Write-Host ''
Write-Host '  ============================================'
Write-Host '   JARBISEO (자비서) 시작 도우미'
Write-Host '  ============================================'
Write-Host ''

# --- 0. Was the ZIP actually extracted? -----------------------------------
if (-not (Test-Path (Join-Path $PSScriptRoot 'package.json'))) {
    Write-Host '  [!] 압축(ZIP) 안에서 바로 실행하신 것 같습니다.'
    Write-Host '      ZIP 파일을 마우스 오른쪽 클릭 -> "압축 풀기"를 먼저 한 다음,'
    Write-Host '      압축 푼 폴더 안에서 다시 더블클릭해 주세요.'
    Wait-Exit 1
}

# --- 1. Node.js check -------------------------------------------------------
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host '  [!] Node.js가 설치되어 있지 않습니다.'
    Write-Host '      지금 열리는 페이지에서 초록색 LTS 버튼을 눌러 설치한 뒤,'
    Write-Host '      이 파일을 다시 더블클릭해 주세요.'
    Start-Process 'https://nodejs.org/ko/download'
    Wait-Exit 1
}
Write-Host "  Node.js 확인: $($node.Source)"

# --- 2. First-run dependency install ----------------------------------------
if (-not (Test-Path (Join-Path $PSScriptRoot 'node_modules'))) {
    Write-Host ''
    Write-Host '  처음 실행 준비 중입니다... 1~2분 정도 걸릴 수 있습니다.'
    & npm install --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) {
        Write-Host ''
        Write-Host '  [!] 설치에 실패했습니다. 인터넷 연결을 확인하고 다시 실행해 주세요.'
        Wait-Exit 1
    }
}

# --- 3. First-run API key setup ----------------------------------------------
if (-not (Test-Path (Join-Path $PSScriptRoot '.env'))) {
    Write-Host ''
    Write-Host '  Anthropic API 키가 필요합니다. (https://console.anthropic.com 에서 발급)'
    Write-Host '  키는 이 컴퓨터의 .env 파일에만 저장되며 외부로 나가지 않습니다.'
    Write-Host ''
    $key = (Read-Host '  API 키를 붙여넣고 Enter').Trim()
    if (-not $key) {
        Write-Host '  [!] 키가 입력되지 않았습니다. 다시 실행해 주세요.'
        Wait-Exit 1
    }
    Set-Content -Path (Join-Path $PSScriptRoot '.env') -Value "ANTHROPIC_API_KEY=$key" -Encoding ASCII
    Write-Host '  저장 완료. (.env 파일은 절대 다른 사람과 공유하지 마세요)'
}

# --- 4. Launch ---------------------------------------------------------------
# Open the browser a moment after the server has had time to boot.
Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile', '-Command', "Start-Sleep 2; Start-Process 'http://localhost:3800'"

Write-Host ''
Write-Host '  ============================================'
Write-Host '   자비서를 시작합니다.'
Write-Host '   브라우저가 자동으로 열립니다: http://localhost:3800'
Write-Host '   이 창은 닫지 마세요. (닫으면 자비서가 종료됩니다)'
Write-Host '  ============================================'
Write-Host ''

& node server.js

# Server stopped (crash or Ctrl+C) — keep the window open so errors are readable.
Write-Host ''
Write-Host '  자비서가 종료되었습니다. 위에 오류 메시지가 있다면 캡처해서 보내 주세요.'
Wait-Exit 0
