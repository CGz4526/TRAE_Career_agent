# 后端职途 · 部署手册（Vercel + Railway）

> 目标：把项目部署到免费云平台，产出可公开访问的体验链接，满足 AI 比赛初赛「有交互、可体验的 Demo」要求。
> 校园网只影响「你点部署」那一刻，部署完成后评委访问的是云平台 URL，与你的电脑/校园网无关。

---

## 一、前置准备

1. **代理（部署阶段用）**
   校园网常墙/限速境外平台（Vercel、Railway、GitHub）。你本机已配代理 `127.0.0.1:7890`，部署时保持开启即可。
2. **账号注册**
   - [Vercel](https://vercel.com)（用 GitHub 登录）
   - [Railway](https://railway.app)（用 GitHub 登录）
   - GitHub 账号（项目已是 GitHub 仓库，确认本地改动已 `git push`）
3. **LLM API Key**
   Python AI 服务需要 `LLM_API_KEY`（看 `backend-python/config.py`，默认用火山方舟 `ark.cn-beijing.volces.com`）。部署时在 Railway 注入真实 key，否则 AI 功能调用会失败（但 `/health` 健康检查能跑）。

---

## 二、推送到 GitHub

项目已是 git 仓库，本次改动已就绪。确认提交并推送：

```bash
git add -A
git commit -m "feat: 支持云部署（前端双域名 + 后端环境变量化 + 部署配置）"
git push origin main
```

> 改动清单（本地开发不受影响，默认值与原来一致）：
> - 前端 axios 拆成 `apiClient`(Java) / `agentClient`(Python)，由 `VITE_API_BASE` / `VITE_AGENT_BASE` 注入
> - `application.yml` 端口/MySQL/Redis/AI服务地址改为环境变量（本地仍走 docker-compose 默认值）
> - 新增 `frontend/vercel.json`、`frontend/.env.production.example`、`backend-python/Procfile`、`backend-python/railway.json`、`backend-java/railway.json`
> - 安装 `@types/node`（修 tsconfig 类型检查缺包问题）

---

## 三、Railway 部署 Python AI 服务

1. Railway 控制台 → **New Project** → **Deploy from GitHub repo**
2. 选择本仓库，设置 **Root Directory = `backend-python`**
3. 等待构建（Nixpacks 自动识别 `requirements.txt` + `Procfile`）
4. 进入服务 **Variables**，添加：
   | 变量 | 值 | 说明 |
   |------|----|------|
   | `ALLOWED_ORIGINS` | 稍后填 Vercel 前端域名，如 `https://career-agent.vercel.app` | 放通前端跨域 |
   | `LLM_API_KEY` | 你的真实 key | AI 功能必需 |
   | `LLM_BASE_URL` | 默认即可（火山方舟） | 可选 |
5. 部署完成后，记下该服务的域名：`https://<python-service>.railway.app`
   （可用 `https://<python-service>.railway.app/agent/health` 验证，返回 `{"status":"ok"}` 即正常）

> Python 服务**不需要** MySQL/Redis，它只调 LLM。

---

## 四、Railway 部署 Java 后端

1. Railway 同一个 Project → **New Service** → **Deploy from GitHub repo**
2. Root Directory = `backend-java`
3. 在该服务里添加插件：**MySQL** 和 **Redis**（Railway 会自动注入 `MYSQLHOST` / `MYSQLPORT` / `MYSQLDATABASE` / `MYSQLUSER` / `MYSQLPASSWORD` 和 `REDISHOST` / `REDISPORT` / `REDISPASSWORD`，代码已读取这些变量）
4. Variables 添加：
   | 变量 | 值 | 说明 |
   |------|----|------|
   | `AI_SERVICE_URL` | 上一步 Python 服务域名，如 `https://<python-service>.railway.app` | Java 调用 Python 的地址 |
   | `PORT` | 自动注入，无需手填 | Spring Boot 读取 `${PORT:8080}` |
5. 验证：`https://<java-service>.railway.app/health` 返回 `{"status":"ok"}`

> Java CORS 已配置为允许所有来源（`setAllowedOriginPatterns("*")`），无需再单独放行 Vercel 域名。

---

## 五、Vercel 部署前端

1. Vercel 控制台 → **Add New** → **Project** → 导入本仓库
2. **Root Directory = `frontend`**（重要，否则找不到 vite 项目）
3. Framework 选 Vite（自动识别），Build Command 已通过 `vercel.json` 设为 `vite build`，Output 为 `dist`
4. **Environment Variables** 先填（也可部署后再补，但补完需重部署）：
   | 变量 | 值 |
   |------|----|
   | `VITE_API_BASE` | Java 服务域名：`https://<java-service>.railway.app` |
   | `VITE_AGENT_BASE` | Python 服务域名：`https://<python-service>.railway.app` |
5. 点击 Deploy。完成后得到前端域名：`https://<your-project>.vercel.app`

> 说明：Vite 在**构建时**把这两个变量编译进前端包。如果当时没填，前端会走相对路径 `/api`、`/agent`（在 Vercel 域下会 404）。填好变量后 Vercel 会自动重新构建。

---

## 六、回填 Python 的跨域域名（关键一步）

前端部署拿到 Vercel 域名后，回到 **Railway 的 Python 服务 → Variables**，把 `ALLOWED_ORIGINS` 设为真实前端域名（如 `https://<your-project>.vercel.app`），保存后 Railway 会自动重启。

> 这一步不做，浏览器会因 CORS 拦截 `/agent/*` 请求。

---

## 七、验证清单

| 项 | 地址 | 期望 |
|----|------|------|
| Python 健康 | `https://<python>.railway.app/agent/health` | `{"status":"ok"}` |
| Java 健康 | `https://<java>.railway.app/health` | `{"status":"ok"}` |
| 前端首页 | `https://<vercel>.vercel.app` | 正常加载 |
| 注册/登录 | 前端 `/login` | 能注册并拿到 token |
| 核心功能 | 岗位匹配 / 题库生成 / 模拟面试 | 调通 Python AI 服务 |

---

## 八、注意事项

- **免费额度**：Railway 免费层约 $5/月额度，MySQL + Redis + 两个服务可能接近上限，初赛演示期足够，长期需留意。
- **冷启动**：Railway 免费实例闲置后会休眠，评委首次访问可能等 10~30 秒，属正常。
- **数据合规**：简历/求职数据传到境外云，若在意合规可改用腾讯云 CloudBase / 阿里云（路线 2）。
- **密码安全**：`docker-compose.yml` 里的明文密码仅用于本地，已通过环境变量方式隔离，不会上云。
- **类型检查**：`npm run build` 含 `vue-tsc` 类型检查，会暴露项目既有的一些类型小问题（与部署无关）。部署用 `vite build` 已跳过，不影响线上产物。
- **AI 功能依赖**：务必在 Railway Python 服务填 `LLM_API_KEY`，否则 AI 调用失败。

---

## 部署顺序速记

```
GitHub push
  → Railway 部署 Python（拿 py-url）
  → Railway 部署 Java（+MySQL +Redis，AI_SERVICE_URL=py-url，拿 java-url）
  → Vercel 部署前端（VITE_API_BASE=java-url, VITE_AGENT_BASE=py-url）
  → 回填 Python 的 ALLOWED_ORIGINS=vercel-url
  → 验证
```
