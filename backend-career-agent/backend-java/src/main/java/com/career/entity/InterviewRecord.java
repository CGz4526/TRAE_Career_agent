package com.career.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 模拟面试记录实体类 —— 对应 interview_records 表
 */
@Data
@TableName(value = "interview_records", autoResultMap = true)
public class InterviewRecord {

    /**
     * 主键 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 用户 ID
     */
    @TableField("user_id")
    private Long userId;

    /**
     * 使用的简历 ID
     */
    @TableField("resume_id")
    private Long resumeId;

    /**
     * 关联的 JD ID
     */
    @TableField("jd_id")
    private Long jdId;

    /**
     * 面试对话记录（JSON 数组）
     */
    @TableField(value = "messages", typeHandler = JacksonTypeHandler.class)
    private List<Map<String, Object>> messages;

    /**
     * 评分报告（JSON 对象）
     */
    @TableField(value = "score_report", typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> scoreReport;

    /**
     * 状态: pending / in_progress / completed
     */
    @TableField("status")
    private String status;

    /**
     * 开始时间
     */
    @TableField("started_at")
    private LocalDateTime startedAt;

    /**
     * 结束时间
     */
    @TableField("ended_at")
    private LocalDateTime endedAt;
}
