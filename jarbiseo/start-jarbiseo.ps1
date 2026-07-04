# JARBISEO one-click launcher (called by 자비서시작.bat)
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}
Set-Location -Path $PSScriptRoot

$Repo   = 'sonarki/VibeStudio_MVP'
$Branch = 'claude/new-session-k9cq8o'
$SubDir = 'jarbiseo'

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

# --- 2. Auto-update from GitHub (best effort; skipped when offline) ----------
function Invoke-AutoUpdate {
    $headers = @{ 'User-Agent' = 'jarbiseo-updater' }
    $branchInfo = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/branches/$Branch" -Headers $headers -TimeoutSec 8
    $sha = $branchInfo.commit.sha
    $stampFile = Join-Path $PSScriptRoot '.last-update'
    $current = ''
    if (Test-Path $stampFile) { $current = (Get-Content $stampFile -Raw).Trim() }
    if ($sha -eq $current) {
        Write-Host '  이미 최신 버전입니다.'
        return
    }

    Write-Host "  새 버전을 내려받는 중... ($($sha.Substring(0,7)))"
    $tree = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/git/trees/${sha}?recursive=1" -Headers $headers -TimeoutSec 15
    $files = @($tree.tree | Where-Object { $_.type -eq 'blob' -and $_.path -like "$SubDir/*" })
    if ($files.Count -eq 0) { throw 'file list empty' }

    # Download everything to a temp folder first so a broken connection
    # can never leave a half-updated install behind.
    $tmp = Join-Path $env:TEMP ("jarbiseo-update-" + $sha.Substring(0, 7))
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    New-Item -ItemType Directory -Path $tmp | Out-Null

    foreach ($f in $files) {
        $rel = $f.path.Substring($SubDir.Length + 1)
        $dest = Join-Path $tmp $rel
        $destDir = Split-Path $dest -Parent
        if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        $escapedPath = ($f.path -split '/' | ForEach-Object { [uri]::EscapeDataString($_) }) -join '/'
        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/$Repo/$sha/$escapedPath" `
            -OutFile $dest -Headers $headers -TimeoutSec 60 -UseBasicParsing
    }

    # Did package.json change? (decides whether npm install must rerun)
    $pkgChanged = $true
    $newPkg = Join-Path $tmp 'package.json'
    $oldPkg = Join-Path $PSScriptRoot 'package.json'
    if ((Test-Path $newPkg) -and (Test-Path $oldPkg)) {
        $pkgChanged = (Get-FileHash $newPkg).Hash -ne (Get-FileHash $oldPkg).Hash
    }

    # Copy file-by-file over the install. .env and node_modules are never
    # in the repo, so they are never touched.
    $preserve = @('jarbiseo.config.json')  # user-edited settings survive updates
    foreach ($f in $files) {
        $rel = $f.path.Substring($SubDir.Length + 1)
        $src = Join-Path $tmp $rel
        $dst = Join-Path $PSScriptRoot $rel
        if (($preserve -contains $rel) -and (Test-Path $dst)) { continue }
        $dstDir = Split-Path $dst -Parent
        if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
        Copy-Item -Path $src -Destination $dst -Force
    }
    Remove-Item $tmp -Recurse -Force
    Set-Content -Path $stampFile -Value $sha -Encoding ASCII

    if ($pkgChanged -and (Test-Path (Join-Path $PSScriptRoot 'node_modules'))) {
        Write-Host '  구성 요소가 변경되어 다시 설치합니다...'
        & npm install --no-audit --no-fund | Out-Null
    }
    Write-Host "  업데이트 완료! (버전 $($sha.Substring(0,7)))"
}

Write-Host '  업데이트 확인 중...'
try {
    Invoke-AutoUpdate
} catch {
    Write-Host '  (업데이트 확인을 건너뜁니다 — 인터넷 연결이 없거나 서버 응답 없음. 현재 버전으로 계속합니다)'
}

# --- 3. First-run dependency install ----------------------------------------
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

# --- 4. First-run API key setup ----------------------------------------------
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

# --- 4b. Optional ElevenLabs key for high-quality voices (asked once) ---------
$envFile = Join-Path $PSScriptRoot '.env'
$envText = Get-Content $envFile -Raw
if ($envText -notmatch 'ELEVENLABS_API_KEY') {
    Write-Host ''
    Write-Host '  (선택) ElevenLabs API 키가 있으면 훨씬 자연스러운 음성을 쓸 수 있습니다.'
    Write-Host '  https://elevenlabs.io 로그인 -> 우측 상단 프로필 -> API Keys 에서 발급.'
    $elKey = (Read-Host '  ElevenLabs API 키를 붙여넣고 Enter (없으면 그냥 Enter)').Trim()
    Add-Content -Path $envFile -Value "ELEVENLABS_API_KEY=$elKey" -Encoding ASCII
    if ($elKey) { Write-Host '  저장 완료. 엘리시아 음성이 활성화됩니다.' }
    else { Write-Host '  건너뜁니다. (나중에 .env 파일에 ELEVENLABS_API_KEY=... 를 추가하면 됩니다)' }
}

# --- 5. Launch ---------------------------------------------------------------
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
