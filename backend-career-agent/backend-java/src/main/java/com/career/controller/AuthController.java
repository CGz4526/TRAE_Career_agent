package com.career.controller;

import com.career.dto.ApiResult;
import com.career.dto.JwtResponse;
import com.career.dto.LoginRequest;
import com.career.dto.RegisterRequest;
import com.career.service.UserService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 认证控制器 —— 注册/登录
 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private static final Logger log = LoggerFactory.getLogger(AuthController.class);

    private final UserService userService;

    public AuthController(UserService userService) {
        this.userService = userService;
    }

    /**
     * 用户注册
     * POST /api/auth/register
     */
    @PostMapping("/register")
    public ApiResult<JwtResponse> register(@Valid @RequestBody RegisterRequest request) {
        try {
            JwtResponse response = userService.register(request);
            return ApiResult.success("注册成功", response);
        } catch (RuntimeException e) {
            log.warn("注册失败: {}", e.getMessage());
            return ApiResult.badRequest(e.getMessage());
        }
    }

    /**
     * 用户登录
     * POST /api/auth/login
     */
    @PostMapping("/login")
    public ApiResult<JwtResponse> login(@Valid @RequestBody LoginRequest request) {
        try {
            JwtResponse response = userService.login(request);
            return ApiResult.success("登录成功", response);
        } catch (RuntimeException e) {
            log.warn("登录失败: {}", e.getMessage());
            return ApiResult.badRequest(e.getMessage());
        }
    }
}
