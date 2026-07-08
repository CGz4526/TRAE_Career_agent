package com.career.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户实体类 —— 对应 users 表
 */
@Data
@TableName("users")
public class User {

    /**
     * 主键 ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 用户名
     */
    @TableField("username")
    private String username;

    /**
     * 密码哈希（BCrypt 加密）
     */
    @TableField("password_hash")
    private String passwordHash;

    /**
     * 邮箱
     */
    @TableField("email")
    private String email;

    /**
     * 昵称
     */
    @TableField("nickname")
    private String nickname;

    /**
     * 头像 URL
     */
    @TableField("avatar")
    private String avatar;

    /**
     * 技术栈，如 "Java,Python,Spring Boot"
     */
    @TableField("tech_stack")
    private String techStack;

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
