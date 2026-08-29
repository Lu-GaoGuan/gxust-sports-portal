$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$archiveName = "sports-portal-deploy.tar.gz"
$archivePath = Join-Path $projectRoot $archiveName
$checksumPath = "$archivePath.sha256"

if (Test-Path -LiteralPath $archivePath) {
    Remove-Item -LiteralPath $archivePath -Force
}
if (Test-Path -LiteralPath $checksumPath) {
    Remove-Item -LiteralPath $checksumPath -Force
}

$arguments = @(
    "-czf", $archiveName,
    "--exclude=backend/db.sqlite3",
    "--exclude=backend/staticfiles",
    "--exclude=backend/**/__pycache__",
    "--exclude=frontend/node_modules",
    "--exclude=frontend/dist",
    "--exclude=deploy/certs/*.pem",
    "--exclude=deploy/certs/*.key",
    "--exclude=deploy/certs/*.crt",
    "--exclude=deploy/nginx/https.conf",
    "backend",
    "frontend",
    "deploy",
    "docker-compose.yml",
    ".dockerignore",
    ".env.production.example",
    "README.md",
    "AGENTS.md"
)

Push-Location $projectRoot
try {
    & tar.exe @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "tar.exe 创建部署包失败，退出码：$LASTEXITCODE"
    }
} finally {
    Pop-Location
}

$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archivePath).Hash.ToLowerInvariant()
"$hash  sports-portal-deploy.tar.gz" | Set-Content -Encoding ASCII -LiteralPath $checksumPath

$archive = Get-Item -LiteralPath $archivePath
Write-Output "部署包：$($archive.FullName)"
Write-Output "大小：$([Math]::Round($archive.Length / 1MB, 2)) MB"
Write-Output "SHA-256：$hash"
