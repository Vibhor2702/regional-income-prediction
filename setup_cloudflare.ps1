Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Cloudflare Deployment Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version
    Write-Host "✅ npm version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Step 1: Installing Frontend Dependencies" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

Set-Location web
Write-Host "Installing Next.js and dependencies..." -ForegroundColor White
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend installation failed!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""
Write-Host "✅ Frontend dependencies installed!" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Step 2: Installing Wrangler CLI" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Installing Wrangler globally..." -ForegroundColor White
npm install -g wrangler

Write-Host ""
Write-Host "✅ Wrangler CLI installed!" -ForegroundColor Green

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Login to Cloudflare:" -ForegroundColor White
Write-Host "   wrangler login" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Deploy API Worker:" -ForegroundColor White
Write-Host "   cd api" -ForegroundColor Cyan
Write-Host "   wrangler deploy" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Deploy Frontend:" -ForegroundColor White
Write-Host "   Option A (GitHub): Push to GitHub, connect via Cloudflare Dashboard" -ForegroundColor Cyan
Write-Host "   Option B (CLI): cd web; npm run build; npx wrangler pages deploy out" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Update API URL:" -ForegroundColor White
Write-Host "   Create web/.env.local with your Worker URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 See CLOUDFLARE_DEPLOYMENT.md for detailed instructions" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Test frontend locally:" -ForegroundColor White
Write-Host "   cd web; npm run dev" -ForegroundColor Cyan
Write-Host "   Visit: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

Write-Host "Start deployment now? (Y/N): " -NoNewline -ForegroundColor Yellow
$deploy = Read-Host

if ($deploy -eq "Y" -or $deploy -eq "y") {
    Write-Host ""
    Write-Host "Starting Wrangler login..." -ForegroundColor Green
    wrangler login
    
    Write-Host ""
    Write-Host "Ready to deploy! Follow the instructions above." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
