package com.career.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 统一响应包装类
 *
 * @param <T> 响应数据类型
 */
@Data
@NoArgsConstructor
public class ApiResult<T> {

    /**
     * 状态码: 200 成功, 400 客户端错误, 500 服务端错误
     */
    private int code;

    /**
     * 响应消息
     */
    private String message;

    /**
     * 响应数据
     */
    private T data;

    public ApiResult(int code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
    }

    /**
     * 成功响应（带数据）
     */
    public static <T> ApiResult<T> success(T data) {
        return new ApiResult<>(200, "操作成功", data);
    }

    /**
     * 成功响应（带消息和数据）
     */
    public static <T> ApiResult<T> success(String message, T data) {
        return new ApiResult<>(200, message, data);
    }

    /**
     * 成功响应（无数据）
     */
    public static <T> ApiResult<T> success() {
        return new ApiResult<>(200, "操作成功", null);
    }

    /**
     * 客户端错误响应
     */
    public static <T> ApiResult<T> error(int code, String message) {
        return new ApiResult<>(code, message, null);
    }

    /**
     * 客户端错误响应（400）
     */
    public static <T> ApiResult<T> badRequest(String message) {
        return new ApiResult<>(400, message, null);
    }

    /**
     * 服务端错误响应（500）
     */
    public static <T> ApiResult<T> serverError(String message) {
        return new ApiResult<>(500, message, null);
    }

    /**
     * 判断是否成功
     */
    public boolean isSuccess() {
        return code == 200;
    }
}
