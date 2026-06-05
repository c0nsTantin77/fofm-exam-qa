# Deploy i2dl-exam-qa to GitHub + enable GitHub Pages.
# Prereq (one-time, interactive):
#     & "C:\Program Files\GitHub CLI\gh.exe" auth login
#       -> GitHub.com -> HTTPS -> "Login with a web browser" -> authorise Git too
# Then just run:  powershell -ExecutionPolicy Bypass -File .\deploy.ps1

$ErrorActionPreference = "Stop"
$OWNER = "c0nsTantin77"
$REPO  = "i2dl-exam-qa"
$DESC  = "I2DL (IN2346) exam Q&A revision deck - TUM"

# locate gh
$gh = (Get-Command gh -ErrorAction SilentlyContinue).Source
if (-not $gh) { $gh = "C:\Program Files\GitHub CLI\gh.exe" }
if (-not (Test-Path $gh)) { throw "gh CLI not found. Install: winget install GitHub.cli" }

# verify auth
& $gh auth status 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "`nNot authenticated. Run this once, then re-run deploy.ps1:" -ForegroundColor Yellow
  Write-Host "    & `"$gh`" auth login" -ForegroundColor Cyan
  exit 1
}

# make sure everything is committed
git add -A
git diff --cached --quiet; if ($LASTEXITCODE -ne 0) {
  git -c user.name=$OWNER -c user.email="linzeqi77@gmail.com" commit -q -m "Update site"
}

# create the repo (idempotent: skip if it already exists) and push
$exists = (& $gh repo view "$OWNER/$REPO" 2>$null)
if ($LASTEXITCODE -ne 0) {
  Write-Host "Creating repo $OWNER/$REPO ..." -ForegroundColor Green
  & $gh repo create "$OWNER/$REPO" --public --source=. --remote=origin --description $DESC --push
} else {
  Write-Host "Repo exists; pushing latest ..." -ForegroundColor Green
  if (-not (git remote 2>$null | Select-String -SimpleMatch origin)) {
    git remote add origin "https://github.com/$OWNER/$REPO.git"
  }
  git push -u origin main
}

# enable GitHub Pages (main branch, root). Ignore error if already enabled.
Write-Host "Enabling GitHub Pages ..." -ForegroundColor Green
try {
  & $gh api -X POST "repos/$OWNER/$REPO/pages" -f "source[branch]=main" -f "source[path]=/" 2>$null
} catch {
  & $gh api -X PUT "repos/$OWNER/$REPO/pages" -f "source[branch]=main" -f "source[path]=/" 2>$null
}

Write-Host "`nDone. Live in ~1 minute at:" -ForegroundColor Green
Write-Host "    https://$OWNER.github.io/$REPO/" -ForegroundColor Cyan
