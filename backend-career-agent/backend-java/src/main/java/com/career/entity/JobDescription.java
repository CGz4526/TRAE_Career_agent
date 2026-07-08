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
 * 岗位描述实体类 —— 对应 job_descriptions 表
 */
@Data
@TableName(value = "job_descriptions", autoResultMap = true)
public class JobDescription {

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
     * 公司名称
     */
    @TableField("company")
    private String company;

    /**
     * 岗位名称
     */
    @TableField("position")
    private String position;

    /**
     * JD 原始文本
     */
    @TableField("raw_text")
    private String rawText;

    /**
     * 结构化岗位需求画像（JSON）
     */
    @TableField(value = "job_profile", typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> jobProfile;

    /**
     * 创建时间
     */
    @TableField("created_at")
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    @TableField("updated_at")
    private LocalDateTime updatedAt;
}
