# Migration Script: Rename pyspread to nxsheet
# This script renames all folders, imports, and references

$projectRoot = "C:\Users\Manoj Konark\Downloads\pyspread-master\pyspread-master"
$pyspreadDir = Join-Path $projectRoot "pyspread"
$nxsheetDir = Join-Path $projectRoot "nxsheet"

Write-Host "Starting migration from pyspread to nxsheet..." -ForegroundColor Green

# Step 1: Rename main pyspread folder to nxsheet
if (Test-Path $pyspreadDir) {
    Write-Host "Renaming folder: pyspread -> nxsheet"
    Rename-Item -Path $pyspreadDir -NewName "nxsheet" -Force
    Write-Host "Folder renamed successfully" -ForegroundColor Green
} else {
    Write-Host "pyspread folder not found" -ForegroundColor Red
    exit 1
}

# Step 2: Update all Python files
Write-Host "`nUpdating Python imports in all files..."
$pythonFiles = Get-ChildItem -Path $nxsheetDir -Filter "*.py" -Recurse
$updateCount = 0

foreach ($file in $pythonFiles) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content
    
    $content = $content -replace "from pyspread\.", "from nxsheet."
    $content = $content -replace "import pyspread\.", "import nxsheet."
    $content = $content -replace "from pyspread import", "from nxsheet import"
    $content = $content -replace "import pyspread([^a-zA-Z])", "import nxsheet`$1"
    
    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content
        $updateCount++
    }
}

Write-Host "Updated $updateCount Python files" -ForegroundColor Green

# Step 3: Update root requirements.txt (remove llama-cpp-python)
$rootReqFile = Join-Path $projectRoot "requirements.txt"
if (Test-Path $rootReqFile) {
    $content = Get-Content $rootReqFile -Raw
    $content = $content -replace "llama-cpp-python.*`n", ""
    Set-Content -Path $rootReqFile -Value $content
    Write-Host "Removed llama-cpp-python from root requirements.txt" -ForegroundColor Green
}

Write-Host "`nMigration Complete!" -ForegroundColor Green
