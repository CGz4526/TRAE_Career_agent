package com.career.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * Agent 任务追踪实体类 —— 对应 agent_tasks 表
 */
@Data
@TableName(value = "agent_tasks", autoResultMap = true)
public class AgentTask {

    /**
     * 主键 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 触发用户 ID
     */
    @TableField("user_id")
    private Long userId;

    /**
     * Agent 类型: job_matcher / resume_optimizer / question_bank / project_story / mock_interview / pipeline
     */
    @TableField("agent_type")
    private String agentType;

    /**
     * 状态: pending / running / completed / failed
     */
    @TableField("status")
    private String status;

    /**
     * 输入数据（JSON）
     */
    @TableField(value = "input_data", typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> inputData;

    /**
     * 输出数据（JSON）
     */
    @TableField(value = "output_data", typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> outputData;

    /**
     * 错误信息
     */
    @TableField("error_message")
    private String errorMessage;

    /**
     * 创建时间
     */
    @TableField("created_at")
    private LocalDateTime createdAt;

    /**
     * 完成时间
     */
    @TableField("completed_at")
    private LocalDateTime completedAt;
}
