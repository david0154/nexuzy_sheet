# Migration Script: Rename pyspread to nexuzy sheet
# This script renames all folders, imports, and references

$projectRoot = "C:\Users\Manoj Konark\Downloads\pyspread-master\pyspread-master"
$pyspreadDir = Join-Path $projectRoot "pyspread"
$nexuzy sheetDir = Join-Path $projectRoot "nexuzy sheet"

Write-Host "Starting migration from pyspread to nexuzy sheet..." -ForegroundColor Green

# Step 1: Rename main pyspread folder to nexuzy sheet
if (Test-Path $pyspreadDir) {
    Write-Host "Renaming folder: pyspread -> nxuzy sheet"
    Rename-Item -Path $pyspreadDir -NewName "nxuzy sheet" -Force
    Write-Host "✓ Folder renamed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ pyspread folder not found at $pyspreadDir" -ForegroundColor Red
    exit 1
}

# Step 2: Update all Python files - replace "from pyspread" with "from nxuzy sheet"
Write-Host "`nUpdating Python imports in all files..."
$pythonFiles = Get-ChildItem -Path $nexuzy sheetDir -Filter "*.py" -Recurse
$updateCount = 0

foreach ($file in $pythonFiles) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content
    
    # Replace: from pyspread.xxx import yyy
    $content = $content -replace 'from pyspread\.', 'from nexuzy sheet.'
    
    # Replace: import pyspread.xxx
    $content = $content -replace 'import pyspread\.', 'import nexuzy sheet.'
    
    # Replace: from pyspread import xxx
    $content = $content -replace 'from pyspread import', 'from nexuzy sheet import'
    
    # Replace: import pyspread
    $content = $content -replace 'import pyspread(?!\w)', 'import nexuzy sheet'
    
    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content
        $updateCount++
        Write-Host "  ✓ Updated: $($file.Name)"
    }
}

Write-Host "✓ Updated $updateCount Python files" -ForegroundColor Green

# Step 3: Update __init__.py
Write-Host "`nUpdating __init__.py with new app name..."
$initFile = Join-Path $nexuzy sheetDir "__init__.py"
if (Test-Path $initFile) {
    $content = Get-Content $initFile -Raw
    $content = $content -replace 'APP_NAME\s*=\s*["\'].*?["\']', "APP_NAME = 'nexuzy sheet'"
    Set-Content -Path $initFile -Value $content
    Write-Host "✓ Updated APP_NAME" -ForegroundColor Green
}

# Step 4: Fix requirements.txt (should only use nexuzy sheet/requirements.txt)
Write-Host "`nFixing requirements.txt files..."
$nexuzy sheetReqFile = Join-Path $nexuzy sheetDir "requirements.txt"
$rootReqFile = Join-Path $projectRoot "requirements.txt"

# Remove llama-cpp-python from root requirements.txt
if (Test-Path $rootReqFile) {
    $content = Get-Content $rootReqFile -Raw
    $content = $content -replace "llama-cpp-python.*`n", ""
    Set-Content -Path $rootReqFile -Value $content
    Write-Host "✓ Removed llama-cpp-python from root requirements.txt" -ForegroundColor Green
}

# Ensure nexuzy sheet/requirements.txt has correct deps
if (Test-Path $nexuzy sheetReqFile) {
    Write-Host "✓ nexuzy sheet/requirements.txt is the primary requirements file" -ForegroundColor Green
}

# Step 5: Update any setup.py or pyproject.toml if they exist
Write-Host "`nUpdating project configuration files..."
$setupFiles = @(
    (Join-Path $projectRoot "setup.py"),
    (Join-Path $projectRoot "pyproject.toml"),
    (Join-Path $projectRoot "setup.cfg")
)

foreach ($setupFile in $setupFiles) {
    if (Test-Path $setupFile) {
        $content = Get-Content $setupFile -Raw
        $originalContent = $content
        
        $content = $content -replace 'pyspread', 'nexuzy sheet'
        
        if ($content -ne $originalContent) {
            Set-Content -Path $setupFile -Value $content
            Write-Host "✓ Updated: $(Split-Path -Leaf $setupFile)" -ForegroundColor Green
        }
    }
}

# Step 6: Update any desktop/config files
Write-Host "`nUpdating config files..."
$configFiles = @(
    (Join-Path $projectRoot "pyspread.desktop"),
    (Join-Path $projectRoot "pyspread.pth")
)

foreach ($configFile in $configFiles) {
    if (Test-Path $configFile) {
        $newName = (Split-Path -Leaf $configFile) -replace 'pyspread', 'nexuzy sheet'
        $newPath = Join-Path (Split-Path $configFile) $newName
        
        $content = Get-Content $configFile -Raw
        $content = $content -replace 'pyspread', 'nexuzy sheet'
        
        Rename-Item -Path $configFile -NewName $newName -Force
        Set-Content -Path $newPath -Value $content
        Write-Host "✓ Renamed and updated: $(Split-Path -Leaf $configFile) -> $newName" -ForegroundColor Green
    }
}

Write-Host "`n" -ForegroundColor Green
Write-Host "═════════════════════════════════════════" -ForegroundColor Green
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "═════════════════════════════════════════" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Test the application: python -m nexuzy sheet"
Write-Host "2. Update any external documentation references from pyspread to nexuzy sheet"
Write-Host "3. Update PATH and PYTHONPATH if needed"
