#!/bin/bash
# 切换到「后端职途」：停 gt-agent，起 后端职途全栈（MySQL/Redis + Python + Java）
set -e
APP_DIR=/opt/app/backend-career-agent
GT_SERVICE=gt-agent.service   # << 改成你 gt-agent 实际的 systemd 服务名（docker/nohup 启动的请相应替换）

echo "==> 停止 gt-agent"
sudo systemctl stop "$GT_SERVICE" || echo "(gt-agent 未以 systemd 管理，跳过停止，请手动停)"

echo "==> 启动 MySQL / Redis（docker，仅后端职途需要）"
cd "$APP_DIR"
sudo docker compose up -d mysql redis

echo "==> 启动 后端职途 Python + Java"
sudo systemctl start career-agent-python.service career-agent-java.service

echo "✅ 已切换到 后端职途 —— 访问 http://career.your.domain"
echo "   健康检查：curl http://127.0.0.1:8001/agent/health  /  curl http://127.0.0.1:8080/health"
