package com.career.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 简历实体类 —— 对应 resumes 表
 */
@Data
@TableName("resumes")
public class Resume {

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
     * 简历标题
     */
    @TableField("title")
    private String title;

    /**
     * 原始简历内容
     */
    @TableField("content")
    private String content;

    /**
     * 优化后简历内容
     */
    @TableField("optimized_content")
    private String optimizedContent;

    /**
     * 状态: draft / optimized
     */
    @TableField("status")
    private String status;

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
