-- ============================================
-- 后端职途 · 数据库初始化脚本
-- ============================================

CREATE DATABASE IF NOT EXISTS career_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE career_agent;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    email VARCHAR(100) DEFAULT '' COMMENT '邮箱',
    nickname VARCHAR(50) DEFAULT '' COMMENT '昵称',
    avatar VARCHAR(255) DEFAULT '' COMMENT '头像URL',
    tech_stack VARCHAR(200) DEFAULT '' COMMENT '技术栈，如 Java,Python',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 简历表
CREATE TABLE IF NOT EXISTS resumes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    title VARCHAR(100) DEFAULT '我的简历' COMMENT '简历标题',
    content TEXT COMMENT '原始简历内容',
    optimized_content TEXT COMMENT '优化后简历内容',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态: draft/optimized',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='简历表';

-- 岗位描述表
CREATE TABLE IF NOT EXISTS job_descriptions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    company VARCHAR(100) DEFAULT '' COMMENT '公司名称',
    position VARCHAR(100) DEFAULT '' COMMENT '岗位名称',
    raw_text TEXT NOT NULL COMMENT 'JD 原始文本',
    job_profile JSON COMMENT '结构化岗位需求画像',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位描述表';

-- 面试记录表
CREATE TABLE IF NOT EXISTS interview_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    resume_id BIGINT COMMENT '使用的简历ID',
    jd_id BIGINT COMMENT '关联的JD ID',
    messages JSON COMMENT '面试对话记录',
    score_report JSON COMMENT '评分报告',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/in_progress/completed',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME DEFAULT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_jd_id (jd_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模拟面试记录表';

-- 题库表
CREATE TABLE IF NOT EXISTS question_banks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    jd_id BIGINT NOT NULL COMMENT '关联的JD ID',
    category VARCHAR(50) NOT NULL COMMENT '分类: 八股文/算法/系统设计/项目深挖',
    difficulty VARCHAR(20) DEFAULT '中等' COMMENT '难度: 简单/中等/困难',
    question TEXT NOT NULL COMMENT '题干',
    answer TEXT COMMENT '标准答案',
    explanation TEXT COMMENT '解析',
    tags JSON COMMENT '知识点标签',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_jd_id (jd_id),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='面试题库表';

-- Agent 任务追踪表
CREATE TABLE IF NOT EXISTS agent_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '触发用户ID',
    agent_type VARCHAR(50) NOT NULL COMMENT 'Agent类型: job_matcher/resume_optimizer/...',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/running/completed/failed',
    input_data JSON COMMENT '输入数据',
    output_data JSON COMMENT '输出数据',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME DEFAULT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent 任务追踪表';

-- Agent 间消息记录表
CREATE TABLE IF NOT EXISTS agent_messages (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_id BIGINT NOT NULL COMMENT '关联任务ID',
    sender_agent VARCHAR(50) NOT NULL COMMENT '发送方Agent',
    receiver_agent VARCHAR(50) NOT NULL COMMENT '接收方Agent',
    content TEXT NOT NULL COMMENT '消息内容',
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent 间消息记录表';
