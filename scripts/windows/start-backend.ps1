param(
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 8000,
  [string]$Environment = "production",
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

# Install backend deps if uvicorn missing
if (-not (Get-Command uvicorn -ErrorAction SilentlyContinue)) {
  Write-Host "Installing backend dependencies..."
  python -m pip install --upgrade pip
  pip install -r backend\requirements.txt
}

# Generate token if not provided
if ([string]::IsNullOrWhiteSpace($Token)) {
  $Token = py -c "import secrets; print(secrets.token_hex(32))"
}

$env:ENVIRONMENT = $Environment
$env:AUTH_BEARER_TOKEN = $Token

Write-Host "ENVIRONMENT=$env:ENVIRONMENT"
Write-Host "AUTH_BEARER_TOKEN set (hidden)"
Write-Host "Starting backend at http://$HostAddress:$Port ..."

uvicorn backend.app.main:app --host $HostAddress --port $Port --reload