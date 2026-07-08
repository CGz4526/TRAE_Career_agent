# ============================================
# 后端职途 · 项目迁移脚本
# 用法: .\migrate.ps1 -TargetDir "D:\CCDevelop"
# ============================================

param(
    [Parameter(Mandatory=$true)]
    [string]$TargetDir
)

$SourceDir = $PSScriptRoot
$ProjectName = "backend-career-agent"
$TargetPath = Join-Path $TargetDir $ProjectName

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  后端职途 · 项目迁移工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "源路径: $SourceDir" -ForegroundColor Yellow
Write-Host "目标路径: $TargetPath" -ForegroundColor Yellow
Write-Host ""

# 1. 检查目标目录
if (Test-Path $TargetPath) {
    Write-Host "[!] 目标目录已存在: $TargetPath" -ForegroundColor Red
    $confirm = Read-Host "是否覆盖？(y/N)"
    if ($confirm -ne 'y') {
        Write-Host "迁移已取消" -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Recurse -Force $TargetPath
}

# 2. 复制项目文件（排除 venv 和 node_modules）
Write-Host "[1/5] 复制项目文件..." -ForegroundColor Green
$excludeDirs = @('venv', 'node_modules', '__pycache__', 'target', '.git')
New-Item -ItemType Directory -Force -Path $TargetPath | Out-Null

$sourceItems = Get-ChildItem -Path $SourceDir -Exclude $excludeDirs
foreach ($item in $sourceItems) {
    Copy-Item -Path $item.FullName -Destination $TargetPath -Recurse -Force
}
Write-Host "  -> 文件复制完成" -ForegroundColor DarkGray

# 3. 重建 Python 虚拟环境
Write-Host "[2/5] 重建 Python 虚拟环境..." -ForegroundColor Green
$pythonVenv = Join-Path $TargetPath "backend-python\venv"
& python -m virtualenv $pythonVenv 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [!] virtualenv 失败，尝试 venv 模块..." -ForegroundColor Yellow
    & python -m venv $pythonVenv 2>&1 | Out-Null
}
& "$pythonVenv\Scripts\python.exe" -m pip install -r "$TargetPath\backend-python\requirements.txt" 2>&1 | Out-Null
Write-Host "  -> Python 依赖安装完成" -ForegroundColor DarkGray

# 4. 安装前端依赖
Write-Host "[3/5] 安装前端依赖..." -ForegroundColor Green
Push-Location "$TargetPath\frontend"
& npm install 2>&1 | Out-Null
Pop-Location
Write-Host "  -> 前端依赖安装完成" -ForegroundColor DarkGray

# 5. 启动 Docker 容器
Write-Host "[4/5] 启动 Docker 容器..." -ForegroundColor Green
Push-Location $TargetPath
& docker compose up -d 2>&1 | Out-Null
Pop-Location
Write-Host "  -> MySQL + Redis 已启动" -ForegroundColor DarkGray

# 6. 生成启动脚本
Write-Host "[5/5] 生成启动脚本..." -ForegroundColor Green
$startScript = @"
# 一键启动所有服务
Write-Host "启动 MySQL + Redis..." -ForegroundColor Cyan
docker compose -f `"$TargetPath\docker-compose.yml`" up -d

Write-Host "启动 Python AI 服务..." -ForegroundColor Cyan
Start-Process -FilePath `"$pythonVenv\Scripts\python.exe`" -ArgumentList '-m','uvicorn','main:app','--host','0.0.0.0','--port','8000','--reload' -WorkingDirectory `"$TargetPath\backend-python`" -NoNewWindow

Write-Host "启动 Java 后端..." -ForegroundColor Cyan
Start-Process -FilePath 'mvn' -ArgumentList 'spring-boot:run' -WorkingDirectory `"$TargetPath\backend-java`" -NoNewWindow

Write-Host "启动前端..." -ForegroundColor Cyan
Start-Process -FilePath 'npx' -ArgumentList 'vite','--host','0.0.0.0','--port','5173' -WorkingDirectory `"$TargetPath\frontend`" -NoNewWindow

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  所有服务已启动！" -ForegroundColor Green
Write-Host "  前端: http://localhost:5173" -ForegroundColor White
Write-Host "  AI服务: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Java后端: http://localhost:8080" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
"@
Set-Content -Path "$TargetPath\start-all.ps1" -Value $startScript -Encoding UTF8
Write-Host "  -> 启动脚本: $TargetPath\start-all.ps1" -ForegroundColor DarkGray

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  迁移完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "项目新路径: $TargetPath" -ForegroundColor White
Write-Host ""
Write-Host "后续启动方式:" -ForegroundColor Yellow
Write-Host "  1. 一键启动: .\$TargetPath\start-all.ps1" -ForegroundColor White
Write-Host "  2. 或分别启动:" -ForegroundColor White
Write-Host "     cd $TargetPath\backend-python ; .\venv\Scripts\python.exe -m uvicorn main:app --port 8000 --reload" -ForegroundColor DarkGray
Write-Host "     cd $TargetPath\frontend ; npx vite --port 5173" -ForegroundColor DarkGray
Write-Host "     cd $TargetPath\backend-java ; mvn spring-boot:run" -ForegroundColor DarkGray
Write-Host ""
