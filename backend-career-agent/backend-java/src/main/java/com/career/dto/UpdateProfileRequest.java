package com.career.dto;

import lombok.Data;

/**
 * 更新用户资料请求
 */
@Data
public class UpdateProfileRequest {

    /**
     * 昵称
     */
    private String nickname;
}
