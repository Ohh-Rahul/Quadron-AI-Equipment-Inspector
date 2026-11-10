$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$stagingRoot = Join-Path $projectRoot "_submission_code"
$packageRoot = Join-Path $stagingRoot "T08_P06_Quadron"
$zipPath = Join-Path $projectRoot "2_Code.zip"

$rootFiles = @(
    "app.py",
    "config.py",
    "requirements.txt",
    "README.md",
    ".gitignore",
    ".env.example"
)

$approvedDirectories = @(
    "src",
    "tests",
    "docs",
    "assets"
)

$forbiddenNamePatterns = @(
    "^\.env$",
    "^secrets\.toml$",
    "^inspection_history\.json$",
    "^2_Code\.zip$",
    "\.zip$",
    "\.pyc$",
    "\.log$",
    "\.tmp$"
)

$forbiddenDirectoryNames = @(
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".ipynb_checkpoints",
    ".vscode",
    ".idea"
)

function Test-ForbiddenFileName {
    param([Parameter(Mandatory = $true)][string]$Name)

    foreach ($pattern in $forbiddenNamePatterns) {
        if ($Name -match $pattern) {
            return $true
        }
    }

    return $false
}

function Test-ForbiddenPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    foreach ($directoryName in $forbiddenDirectoryNames) {
        if ($Path -match [regex]::Escape("\$directoryName\")) {
            return $true
        }
    }

    return $false
}

function Test-SuspiciousContent {
    param([Parameter(Mandatory = $true)][string]$Path)

    $extension = [IO.Path]::GetExtension($Path).ToLowerInvariant()
    $textExtensions = @(".py", ".txt", ".md", ".json", ".toml", ".ini", ".cfg", ".yaml", ".yml", ".ps1")
    if ($textExtensions -notcontains $extension) {
        return
    }

    $content = Get-Content -LiteralPath $Path -Raw
    $patterns = @(
        "-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "gh[pousr]_[A-Za-z0-9_]{20,}",
        "sk-[A-Za-z0-9]{20,}",
        "Bearer\s+[A-Za-z0-9._-]{20,}",
        "https://[^ \r\n]+\.services\.ai\.azure\.com/api/projects/(?!YOUR-PROJECT)"
    )

    foreach ($pattern in $patterns) {
        if ($content -match $pattern) {
            throw "Suspicious secret-like content found in '$Path'. Review it before packaging."
        }
    }
}

function Copy-ApprovedFile {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string]$DestinationRoot
    )

    $sourcePath = Join-Path $projectRoot $RelativePath
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        throw "Required file is missing: $RelativePath"
    }

    if (Test-ForbiddenFileName -Name ([IO.Path]::GetFileName($sourcePath))) {
        throw "Refusing to package forbidden file: $RelativePath"
    }

    Test-SuspiciousContent -Path $sourcePath

    $destinationPath = Join-Path $DestinationRoot $RelativePath
    $destinationDirectory = Split-Path -Parent $destinationPath
    New-Item -ItemType Directory -Force -Path $destinationDirectory | Out-Null
    Copy-Item -LiteralPath $sourcePath -Destination $destinationPath -Force
}

function Copy-ApprovedDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$RelativeDirectory,
        [Parameter(Mandatory = $true)][string]$DestinationRoot
    )

    $sourceDirectory = Join-Path $projectRoot $RelativeDirectory
    if (-not (Test-Path -LiteralPath $sourceDirectory -PathType Container)) {
        return
    }

    $files = @(Get-ChildItem -LiteralPath $sourceDirectory -File -Recurse -Force)
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($projectRoot.Length).TrimStart("\")
        if ((Test-ForbiddenFileName -Name $file.Name) -or (Test-ForbiddenPath -Path $file.FullName)) {
            continue
        }

        Test-SuspiciousContent -Path $file.FullName
        $destinationPath = Join-Path $DestinationRoot $relativePath
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destinationPath) | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $destinationPath -Force
    }
}

if ((Get-Content -LiteralPath (Join-Path $projectRoot ".env.example") -Raw) -notmatch
    "(?m)^FOUNDRY_PROJECT_ENDPOINT=https://YOUR-RESOURCE\.services\.ai\.azure\.com/api/projects/YOUR-PROJECT\s*$") {
    throw ".env.example does not contain the required placeholder endpoint."
}

if ((Get-Content -LiteralPath (Join-Path $projectRoot ".env.example") -Raw) -notmatch
    "(?m)^FOUNDRY_AGENT_NAME=Lab-Equipment-Inspector-T08\s*$") {
    throw ".env.example does not contain the required agent name."
}

if (Test-Path -LiteralPath $stagingRoot) {
    Remove-Item -LiteralPath $stagingRoot -Recurse -Force
}
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
New-Item -ItemType Directory -Force -Path $packageRoot | Out-Null

foreach ($file in $rootFiles) {
    Copy-ApprovedFile -RelativePath $file -DestinationRoot $packageRoot
}

foreach ($directory in $approvedDirectories) {
    Copy-ApprovedDirectory -RelativeDirectory $directory -DestinationRoot $packageRoot
}

Copy-ApprovedFile -RelativePath "data\checklists.json" -DestinationRoot $packageRoot
Copy-ApprovedDirectory -RelativeDirectory "data\test_images" -DestinationRoot $packageRoot

Compress-Archive -LiteralPath $packageRoot -DestinationPath $zipPath -CompressionLevel Optimal

$requiredArchiveEntries = @(
    "T08_P06_Quadron\app.py",
    "T08_P06_Quadron\config.py",
    "T08_P06_Quadron\requirements.txt",
    "T08_P06_Quadron\README.md",
    "T08_P06_Quadron\.env.example",
    "T08_P06_Quadron\data\checklists.json"
)
$archiveEntries = @( [IO.Compression.ZipFile]::OpenRead($zipPath).Entries | ForEach-Object { $_.FullName } )
$archive = [IO.Compression.ZipFile]::OpenRead($zipPath)
try {
    foreach ($requiredEntry in $requiredArchiveEntries) {
        if ($archiveEntries -notcontains $requiredEntry) {
            throw "ZIP validation failed; missing '$requiredEntry'."
        }
    }

    foreach ($entry in $archive.Entries) {
        $normalizedName = $entry.FullName.Replace("/", "\")
        if ($normalizedName -match "(^|\\)(\.env|\.git|\.venv|venv|env|__pycache__|\.vscode|\.idea)(\\|$)" -or
            $normalizedName -match "inspection_history\.json$|\.pyc$|\.zip$") {
            throw "ZIP validation failed; forbidden entry '$($entry.FullName)' is present."
        }
    }
}
finally {
    $archive.Dispose()
}

$includedFiles = @(Get-ChildItem -LiteralPath $packageRoot -File -Recurse | Sort-Object FullName)
Write-Output "Created: $zipPath"
Write-Output ("Size: {0:N0} bytes" -f (Get-Item -LiteralPath $zipPath).Length)
Write-Output ("Files included: {0}" -f $includedFiles.Count)
$includedFiles | ForEach-Object {
    Write-Output (" - " + $_.FullName.Substring($packageRoot.Length).TrimStart("\"))
}
