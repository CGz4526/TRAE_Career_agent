"""
预设角色卡系统 —— 8 个通用技术岗位角色卡
每个角色卡包含完整的技术画像，各模块可直接使用无需依赖岗位匹配
"""
from models.schemas import JobProfile
from typing import List


# ==================== 预设角色卡定义 ====================
PRESET_ROLE_CARDS = [
    {
        "id": "java-backend",
        "name": "Java 后端开发工程师",
        "icon": "☕",
        "color": "#f89820",
        "description": "专注于 Java 企业级后端开发，精通 Spring 生态",
        "profile": {
            "position": "Java 后端开发工程师",
            "tech_stack": ["Java", "Spring Boot", "Spring Cloud", "MyBatis", "MySQL", "Redis", "Kafka", "JVM"],
            "experience_years": 3,
            "education": "本科及以上",
            "core_skills": [
                "Java 并发编程", "JVM 调优", "Spring Boot/Cloud 微服务",
                "MySQL 索引优化与分库分表", "Redis 缓存设计",
                "消息队列 Kafka/RocketMQ", "分布式锁与分布式事务"
            ],
            "soft_skills": ["沟通协作", "代码规范", "技术文档撰写", "问题排查"],
            "bonus_items": ["高并发系统设计经验", "DevOps/CI/CD", "K8s 容器化", "开源项目贡献"],
            "key_responsibilities": [
                "后端业务系统设计与开发",
                "数据库设计与接口性能优化",
                "微服务架构设计与治理",
                "线上问题排查与系统稳定性保障"
            ]
        },
        "interview_focus": [
            "Java 基础（集合、并发、IO、JVM）",
            "Spring 原理（IOC、AOP、事务）",
            "数据库（索引、锁、优化、分库分表）",
            "中间件（Redis、Kafka、Zookeeper）",
            "分布式（CAP、一致性、限流、熔断）",
            "系统设计（秒杀、短链、消息推送）"
        ]
    },
    {
        "id": "python-backend",
        "name": "Python 后端开发工程师",
        "icon": "🐍",
        "color": "#3776ab",
        "description": "专注于 Python 后端开发，精通 Web 框架与数据处理",
        "profile": {
            "position": "Python 后端开发工程师",
            "tech_stack": ["Python", "Django", "FastAPI", "Flask", "PostgreSQL", "Redis", "Celery", "Docker"],
            "experience_years": 2,
            "education": "本科及以上",
            "core_skills": [
                "Python 异步编程", "Django/FastAPI Web 开发",
                "PostgreSQL/MySQL 数据库设计", "Redis 缓存策略",
                "Celery 异步任务", "RESTful API 设计",
                "Python 性能优化与 GIL 理解"
            ],
            "soft_skills": ["快速学习", "技术文档", "跨团队协作", "代码审查"],
            "bonus_items": ["机器学习/AI 工程化", "K8s 部署", "微服务架构", "数据可视化"],
            "key_responsibilities": [
                "后端 API 设计与开发",
                "数据处理管道搭建",
                "异步任务系统设计",
                "系统性能监控与优化"
            ]
        },
        "interview_focus": [
            "Python 基础（GIL、装饰器、生成器、元类）",
            "Web 框架（Django ORM、FastAPI 异步、中间件）",
            "数据库（ORM 优化、索引、事务）",
            "异步编程（asyncio、Celery、消息队列）",
            "设计模式与代码架构",
            "系统设计（高并发 API、数据管道）"
        ]
    },
    {
        "id": "go-backend",
        "name": "Go 后端开发工程师",
        "icon": "🐹",
        "color": "#00add8",
        "description": "专注于 Go 语言高性能后端开发",
        "profile": {
            "position": "Go 后端开发工程师",
            "tech_stack": ["Go", "Gin", "GORM", "MySQL", "Redis", "Kafka", "gRPC", "K8s"],
            "experience_years": 2,
            "education": "本科及以上",
            "core_skills": [
                "Go 并发编程（goroutine、channel）", "Gin/Echo Web 框架",
                "gRPC 微服务通信", "MySQL/Redis 数据存储",
                "Go 性能调优（pprof）", "容器化与 K8s 部署",
                "分布式系统设计"
            ],
            "soft_skills": ["技术钻研", "简洁沟通", "工程化思维", "Code Review"],
            "bonus_items": ["开源贡献", "云原生经验", "Service Mesh", "eBPF"],
            "key_responsibilities": [
                "高性能后端服务开发",
                "微服务架构设计与实现",
                "系统性能优化",
                "云原生基础设施建设"
            ]
        },
        "interview_focus": [
            "Go 基础（slice、map、channel、context）",
            "并发编程（goroutine 调度、sync 包、内存模型）",
            "Web 框架（Gin 路由、中间件、参数校验）",
            "微服务（gRPC、Protobuf、服务发现）",
            "性能优化（pprof、逃逸分析、GC）",
            "系统设计（高并发网关、消息系统）"
        ]
    },
    {
        "id": "frontend",
        "name": "前端开发工程师",
        "icon": "🌐",
        "color": "#e34c26",
        "description": "专注于 Web 前端开发，精通 React/Vue 生态",
        "profile": {
            "position": "前端开发工程师",
            "tech_stack": ["JavaScript", "TypeScript", "React", "Vue", "Webpack", "Vite", "Node.js", "CSS3"],
            "experience_years": 2,
            "education": "本科及以上",
            "core_skills": [
                "JavaScript/TypeScript 深入", "React Hooks 与组件设计",
                "Vue3 Composition API", "Webpack/Vite 构建工具",
                "CSS 布局与动画", "性能优化（懒加载、虚拟列表）",
                "Node.js BFF 层开发"
            ],
            "soft_skills": ["用户体验意识", "设计协作", "技术分享", "文档习惯"],
            "bonus_items": ["跨端开发（React Native/小程序）", "WebGL/Three.js", "低代码平台", "开源贡献"],
            "key_responsibilities": [
                "Web 前端页面开发与维护",
                "前端架构设计与组件库建设",
                "前端性能优化",
                "与后端协作完成产品功能"
            ]
        },
        "interview_focus": [
            "JS 基础（闭包、原型链、事件循环、异步）",
            "框架原理（React Fiber、Vue 响应式、Diff 算法）",
            "工程化（Webpack、Vite、Tree-shaking、按需加载）",
            "CSS（BFC、Flex、Grid、动画、主题切换）",
            "性能优化（Lighthouse、首屏、运行时）",
            "系统设计（组件库、微前端、SSR）"
        ]
    },
    {
        "id": "algorithm",
        "name": "算法工程师",
        "icon": "🧮",
        "color": "#9b59b6",
        "description": "专注于机器学习/深度学习算法研发",
        "profile": {
            "position": "算法工程师",
            "tech_stack": ["Python", "PyTorch", "TensorFlow", "Scikit-learn", "Pandas", "NumPy", "SQL", "Docker"],
            "experience_years": 2,
            "education": "硕士及以上",
            "core_skills": [
                "机器学习算法（分类/回归/聚类）", "深度学习模型设计与训练",
                "NLP/CV 领域知识", "特征工程与数据处理",
                "模型部署与推理优化", "A/B 测试与效果评估",
                "分布式训练"
            ],
            "soft_skills": ["论文阅读", "逻辑思维", "跨部门沟通", "技术写作"],
            "bonus_items": ["顶会论文发表", "Kaggle 竞赛经历", "大模型微调经验", "推荐系统经验"],
            "key_responsibilities": [
                "算法模型设计与训练",
                "特征工程与数据管道建设",
                "模型部署与线上效果优化",
                "算法技术调研与落地"
            ]
        },
        "interview_focus": [
            "数学基础（线性代数、概率论、优化理论）",
            "机器学习（LR、SVM、决策树、集成学习、正则化）",
            "深度学习（CNN、RNN、Transformer、注意力机制）",
            "工程能力（PyTorch、模型压缩、推理优化）",
            "业务场景（推荐、搜索、广告、NLP/CV）",
            "系统设计（特征平台、模型服务、AB 测试）"
        ]
    },
    {
        "id": "fullstack",
        "name": "全栈开发工程师",
        "icon": "⚡",
        "color": "#2ecc71",
        "description": "精通前后端全链路开发，独立交付完整产品",
        "profile": {
            "position": "全栈开发工程师",
            "tech_stack": ["JavaScript", "TypeScript", "Vue/React", "Node.js", "Java/Python", "MySQL", "Redis", "Docker"],
            "experience_years": 3,
            "education": "本科及以上",
            "core_skills": [
                "前端开发（React/Vue + TypeScript）", "后端开发（Node.js/Java/Python）",
                "数据库设计与管理", "DevOps 与 CI/CD",
                "系统架构设计", "API 设计与文档",
                "前端性能优化与后端高并发处理"
            ],
            "soft_skills": ["独立交付", "产品思维", "全链路排查", "技术选型"],
            "bonus_items": ["开源全栈项目", "云原生经验", "技术团队管理", "产品设计"],
            "key_responsibilities": [
                "全栈功能开发与交付",
                "系统架构设计与技术选型",
                "DevOps 流程建设",
                "跨团队技术协作"
            ]
        },
        "interview_focus": [
            "前端基础（JS/TS、框架原理、工程化）",
            "后端基础（API 设计、数据库、并发）",
            "架构设计（微服务、DDD、CQRS）",
            "DevOps（Docker、K8s、CI/CD、监控）",
            "系统设计（全栈项目架构、技术选型）",
            "产品思维（需求分析、用户体验）"
        ]
    },
    {
        "id": "bigdata",
        "name": "大数据开发工程师",
        "icon": "📊",
        "color": "#f39c12",
        "description": "专注于大数据处理与分析平台开发",
        "profile": {
            "position": "大数据开发工程师",
            "tech_stack": ["Java", "Scala", "Python", "Hadoop", "Spark", "Flink", "Kafka", "Hive"],
            "experience_years": 2,
            "education": "本科及以上",
            "core_skills": [
                "Hadoop/Spark/Flink 大数据框架", "Kafka 消息队列",
                "Hive 数据仓库设计", "ETL 数据管道开发",
                "SQL 与数据分析", "数据治理与数据质量",
                "实时计算与离线计算"
            ],
            "soft_skills": ["数据敏感", "逻辑分析", "跨团队协作", "文档规范"],
            "bonus_items": ["数据中台经验", "实时数仓", "OLAP 引擎（ClickHouse/Doris）", "数据治理"],
            "key_responsibilities": [
                "大数据平台开发与维护",
                "ETL 管道设计与优化",
                "数据仓库建设",
                "实时/离线计算任务开发"
            ]
        },
        "interview_focus": [
            "Hadoop 生态（HDFS、YARN、MapReduce）",
            "Spark（RDD、DataFrame、Spark SQL、调优）",
            "Flink（窗口、状态、Watermark、Exactly-Once）",
            "Kafka（分区、副本、Exactly-Once、消息有序）",
            "数据仓库（分层模型、维度建模、缓慢变化维）",
            "系统设计（实时数仓、离线数仓、数据湖）"
        ]
    },
    {
        "id": "devops",
        "name": "DevOps 工程师",
        "icon": "🔧",
        "color": "#e74c3c",
        "description": "专注于 DevOps 与云原生基础设施建设",
        "profile": {
            "position": "DevOps 工程师",
            "tech_stack": ["Linux", "Docker", "Kubernetes", "Jenkins", "Python", "Go", "Terraform", "Prometheus"],
            "experience_years": 2,
            "education": "本科及以上",
            "core_skills": [
                "Linux 系统管理", "Docker 容器化",
                "Kubernetes 集群管理", "CI/CD 流水线设计",
                "基础设施即代码（Terraform/Ansible）", "监控告警系统",
                "Shell/Python/Go 自动化脚本"
            ],
            "soft_skills": ["运维意识", "应急响应", "文档习惯", "跨团队沟通"],
            "bonus_items": ["Service Mesh", "云厂商认证", "安全运维", "成本优化"],
            "key_responsibilities": [
                "CI/CD 流水线建设与维护",
                "容器化与 K8s 平台运维",
                "监控告警与故障排查",
                "基础设施自动化"
            ]
        },
        "interview_focus": [
            "Linux（进程、内存、网络、文件系统、Shell）",
            "Docker（镜像、容器、网络、存储、Dockerfile）",
            "K8s（Pod、Deployment、Service、Ingress、调度、存储）",
            "CI/CD（Jenkins、GitLab CI、ArgoCD）",
            "监控（Prometheus、Grafana、ELK、链路追踪）",
            "系统设计（微服务部署、灰度发布、故障自愈）"
        ]
    }
]


def get_all_role_cards() -> List[dict]:
    """获取所有预设角色卡"""
    return PRESET_ROLE_CARDS


def get_role_card_by_id(card_id: str) -> dict | None:
    """根据 ID 获取角色卡"""
    for card in PRESET_ROLE_CARDS:
        if card["id"] == card_id:
            return card
    return None


def role_card_to_profile(card: dict) -> JobProfile:
    """将角色卡转换为 JobProfile（供其他 Agent 使用）"""
    return JobProfile(**card["profile"])


def create_user_role_card(job_profile: JobProfile) -> dict:
    """
    从岗位匹配结果生成用户专属角色卡
    类似微调效果：基于 JD 画像定制角色卡
    """
    return {
        "id": "user-custom",
        "name": f"专属角色 · {job_profile.position}",
        "icon": "🎯",
        "color": "#4f8cff",
        "description": f"基于岗位 JD 分析生成的专属角色卡，精准匹配 {job_profile.position} 岗位要求",
        "profile": job_profile.model_dump(),
        "interview_focus": [
            f"{tech} 深入考察" for tech in job_profile.tech_stack[:5]
        ] + [
            f"{skill} 实战考察" for skill in job_profile.core_skills[:3]
        ]
    }
