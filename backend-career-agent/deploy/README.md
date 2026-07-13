# 后端职途 · 腾讯云轻量 2核2G 部署（与 gt-agent 错开切换）

> 设计目标：服务器 2核2G 已跑 gt-agent。本方案让两个项目**错开运行**——同一时刻只跑一个，
> 用切换脚本一键切换，OOM 风险归零。nginx 常驻，按子域名分流。

---

## 目录结构

```
deploy/
├── README.md                      # 本文件
├── systemd/
│   ├── career-agent-python.service
│   └── career-agent-java.service
├── scripts/
│   ├── switch-to-career.sh        # 切到 后端职途
│   └── switch-to-gt.sh            # 切回 gt-agent
├── nginx/
│   └── career-agent.conf          # 后端职途 nginx server block（子域名）
└── env/
    ├── python.env.example
    └── java.env.example
```

---

## 上服务器后的操作步骤

### 0. 前置（服务器上）
- 已装：git / python3 / docker + docker-compose / nginx / JDK 17（Java 运行用，无需 Maven）
- 把本仓库传到 `/opt/app/backend-career-agent`（路径与下方配置一致，若改路径请同步改各文件里的路径）

### 1. Python 依赖（独立 venv，避免与 gt-agent 的 paddle/numpy 冲突）
```bash
python3 -m venv /opt/venvs/career-agent
source /opt/venvs/career-agent/bin/activate
pip install --upgrade pip
pip install -r /opt/app/backend-career-agent/backend-python/requirements.txt
deactivate
```

### 2. 配置环境变量
```bash
cd /opt/app/backend-career-agent/deploy/env
cp python.env.example python.env   # 然后编辑，填入真实 LLM_API_KEY，改 career.your.domain
cp java.env.example   java.env     # 一般默认值即可，端口与 docker-compose 对应
```

### 3. 构建前端（关键：用相对路径，让 nginx 能分流）
在本机（或服务器装 node 后）构建：
```bash
cd frontend
export VITE_API_BASE=/api
export VITE_AGENT_BASE=/agent
npm install && npm run build        # 产出 dist/
```
把 `dist/` 传到服务器 `/opt/app/backend-career-agent/frontend/dist`。

### 4. 构建 Java jar（建议本机打包，避免服务器跑 Maven 吃内存）
本机：
```bash
cd backend-java
mvn clean package -DskipTests       # 产出 target/backend-java-0.1.0.jar
```
把 `target/backend-java-0.1.0.jar` 传到服务器 `backend-java/target/` 下。
（若服务器已装 JDK17，也可直接传整个 backend-java 源码 + jar。）

### 5. 放 systemd 单元
```bash
sudo cp /opt/app/backend-career-agent/deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 6. 放 nginx 配置
```bash
sudo cp /opt/app/backend-career-agent/deploy/nginx/career-agent.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo nginx -s reload
```
> gt-agent 原有的 nginx 配置保留不动；它和本配置的 `server_name` 不同（子域名），互不冲突。

### 7. 权限
```bash
sudo chown -R www-data:www-data /opt/app/backend-career-agent
sudo chmod +x /opt/app/backend-career-agent/deploy/scripts/*.sh
```

---

## 日常使用：一键切换

```bash
# 用 后端职途（自动停 gt-agent，起 MySQL/Redis + Python + Java）
sudo /opt/app/backend-career-agent/deploy/scripts/switch-to-career.sh

# 用 gt-agent（自动停 后端职途 全栈并释放 MySQL/Redis 内存，起 gt-agent）
sudo /opt/app/backend-career-agent/deploy/scripts/switch-to-gt.sh
```

> ⚠️ 切换脚本里的 `gt-agent.service` 是占位名，请改成你 gt-agent **实际的 systemd 服务名**；
> 若 gt-agent 是用 docker 或 nohup 起的，请相应改脚本里的启动/停止命令。

---

## 折中方案（推荐个人用）：轻量核心常驻 + 重型按需

不想每次切换、又怕 gt-agent OCR 高峰 OOM，可这样：
- **常驻**：gt-agent + 后端职途「Python AI + 前端」（已证并行可行 ~1.1–1.4GB）
- **按需起停**：仅在需要登录/账号/持久化时
  ```bash
  sudo docker compose up -d mysql redis
  sudo systemctl start career-agent-java.service
  ```
  用完释放：
  ```bash
  sudo systemctl stop career-agent-java.service
  sudo docker compose down
  ```

---

## 验证清单

| 项 | 命令 | 期望 |
|----|------|------|
| Python 健康 | `curl http://127.0.0.1:8001/agent/health` | `{"status":"ok",...}` |
| Java 健康 | `curl http://127.0.0.1:8080/health` | `{"status":"ok"}` |
| 前端 | 浏览器开 `http://career.your.domain` | 正常加载 |
| 内存 | `free -h` | 单项目运行时 < 1.6GB，无 OOM |

---

## 风险与注意

- 切换有冷启延迟：MySQL ~10–30s、JVM ~5–10s，整套切过去约 30–60s 才完全就绪。
- 同时只能访问一个项目（错开运行的本质代价）。
- gt-agent 的 service 名 / 启动方式需你按实际情况对齐脚本。
- 数据不丢：MySQL/Redis 用 docker volume 持久化，停了再起数据还在。
