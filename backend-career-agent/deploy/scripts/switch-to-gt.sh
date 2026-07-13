#!/bin/bash
# 切换到「gt-agent」：停 后端职途全栈并释放 MySQL/Redis 内存，起 gt-agent
set -e
APP_DIR=/opt/app/backend-career-agent
GT_SERVICE=gt-agent.service   # << 改成你 gt-agent 实际的 systemd 服务名

echo "==> 停止 后端职途 Python + Java"
sudo systemctl stop career-agent-python.service career-agent-java.service || true

echo "==> 停止 MySQL / Redis，把内存还给 gt-agent"
cd "$APP_DIR"
sudo docker compose down || true

echo "==> 启动 gt-agent"
sudo systemctl start "$GT_SERVICE" || echo "(请按你的实际方式启动 gt-agent)"

echo "✅ 已切换到 gt-agent —— 访问 http://gt.your.domain"
