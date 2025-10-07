Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   GitHub Repository Setup for Your Project" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Get GitHub username
Write-Host "Enter your GitHub username: " -NoNewline -ForegroundColor Yellow
$username = Read-Host

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "❌ Username cannot be empty!" -ForegroundColor Red
    exit 1
}

$repoName = "regional-income-prediction"
$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Step 1: Create Repository on GitHub" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. Open: https://github.com/new" -ForegroundColor White
Write-Host "2. Repository name: $repoName" -ForegroundColor White
Write-Host "3. Description: Machine learning project predicting U.S. regional income" -ForegroundColor White
Write-Host "4. Choose Public or Private" -ForegroundColor White
Write-Host "5. DO NOT initialize with README (we have it already)" -ForegroundColor Yellow
Write-Host "6. Click 'Create repository'" -ForegroundColor White
Write-Host ""
Write-Host "Press any key after creating the repository..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Step 2: Connecting Local to GitHub" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Check if remote already exists
$remoteExists = git remote | Select-String -Pattern "origin" -Quiet
if ($remoteExists) {
    Write-Host "⚠️  Remote 'origin' already exists. Removing..." -ForegroundColor Yellow
    git remote remove origin
}

# Add remote
Write-Host "Adding remote repository..." -ForegroundColor White
git remote add origin $repoUrl

# Verify
$remote = git remote -v
Write-Host "✅ Remote added successfully!" -ForegroundColor Green
Write-Host $remote
Write-Host ""

# Rename branch to main if needed
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "Renaming branch to 'main'..." -ForegroundColor White
    git branch -M main
    Write-Host "✅ Branch renamed to 'main'" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Step 3: Pushing to GitHub" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pushing your code to GitHub..." -ForegroundColor White
Write-Host ""

# Push
try {
    git push -u origin main 2>&1 | Write-Host
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "   ✅ SUCCESS! Your project is on GitHub!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 View your repository at:" -ForegroundColor White
    Write-Host "   https://github.com/$username/$repoName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 Project Statistics:" -ForegroundColor White
    Write-Host "   - 38 files committed" -ForegroundColor White
    Write-Host "   - 27,680 ZIP codes analyzed" -ForegroundColor White
    Write-Host "   - 94.5% model accuracy" -ForegroundColor White
    Write-Host "   - 4 ML models trained" -ForegroundColor White
    Write-Host ""
    Write-Host "🎉 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Add repository topics on GitHub (machine-learning, xgboost, etc.)" -ForegroundColor White
    Write-Host "   2. Create a release (v1.0.0)" -ForegroundColor White
    Write-Host "   3. Share your project!" -ForegroundColor White
    Write-Host ""
    
    # Open in browser
    Write-Host "Open repository in browser? (Y/N): " -NoNewline -ForegroundColor Yellow
    $openBrowser = Read-Host
    if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
        Start-Process "https://github.com/$username/$repoName"
    }
}
catch {
    Write-Host ""
    Write-Host "❌ Push failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Authentication required - GitHub may need a Personal Access Token" -ForegroundColor White
    Write-Host "2. Repository doesn't exist - Make sure you created it on GitHub" -ForegroundColor White
    Write-Host "3. Network issues - Check your internet connection" -ForegroundColor White
    Write-Host ""
    Write-Host "Error details:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "See GITHUB_PUSH_GUIDE.md for troubleshooting help" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
