param(
  [string]$BackendUrl = "http://127.0.0.1:8000",
  [string]$Token = ""
)

$ErrorActionPreference = "Stop"

# Ensure we are in repo root (adjust if needed)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
Set-Location $RepoRoot

# Activate venv if present
$venvActivate = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) { . $venvActivate }

# Install if streamlit missing
if (-not (Get-Command streamlit -ErrorAction SilentlyContinue)) {
  Write-Host "Installing Streamlit..."
  python -m pip install --upgrade pip
  pip install -r backend\requirements.txt
  if (Test-Path "requirements.txt") { pip install -r requirements.txt }
}

# Reuse provided token or prompt/generate
if ([string]::IsNullOrWhiteSpace($Token)) {
  $Token = Read-Host -Prompt "Enter AUTH_BEARER_TOKEN (leave blank to auto-generate)"
  if ([string]::IsNullOrWhiteSpace($Token)) {
    $Token = py -c "import secrets; print(secrets.token_hex(32))"
  }
}

$env:AUTH_BEARER_TOKEN = $Token
$env:BACKEND_URL = $BackendUrl

Write-Host "Starting Streamlit with BACKEND_URL=$BackendUrl ..."

streamlit run streamlit_app.py