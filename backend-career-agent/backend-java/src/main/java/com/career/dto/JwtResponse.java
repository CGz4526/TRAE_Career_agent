package com.career.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * JWT 认证响应 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class JwtResponse {

    /**
     * JWT Token
     */
    private String token;

    /**
     * Token 类型
     */
    private String type;

    /**
     * 用户名
     */
    private String username;

    /**
     * 用户 ID
     */
    private Long userId;
}
