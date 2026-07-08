package com.career.controller;

import com.career.dto.ApiResult;
import com.career.entity.Resume;
import com.career.service.ResumeService;
import com.career.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 简历控制器 —— 简历 CRUD
 */
@RestController
@RequestMapping("/api/resumes")
public class ResumeController {

    private static final Logger log = LoggerFactory.getLogger(ResumeController.class);

    private final ResumeService resumeService;
    private final UserService userService;

    public ResumeController(ResumeService resumeService, UserService userService) {
        this.resumeService = resumeService;
        this.userService = userService;
    }

    /**
     * 获取当前用户的所有简历
     * GET /api/resumes
     */
    @GetMapping
    public ApiResult<List<Resume>> list() {
        try {
            Long userId = userService.getCurrentUserId();
            return ApiResult.success(resumeService.listByUserId(userId));
        } catch (RuntimeException e) {
            return ApiResult.serverError(e.getMessage());
        }
    }

    /**
     * 获取指定简历详情
     * GET /api/resumes/{id}
     */
    @GetMapping("/{id}")
    public ApiResult<Resume> getById(@PathVariable Long id) {
        try {
            Long userId = userService.getCurrentUserId();
            return ApiResult.success(resumeService.getById(id, userId));
        } catch (RuntimeException e) {
            return ApiResult.badRequest(e.getMessage());
        }
    }

    /**
     * 创建简历
     * POST /api/resumes
     */
    @PostMapping
    public ApiResult<Resume> create(@RequestBody Resume resume) {
        try {
            Long userId = userService.getCurrentUserId();
            resume.setUserId(userId);
            return ApiResult.success("简历创建成功", resumeService.create(resume));
        } catch (RuntimeException e) {
            return ApiResult.serverError(e.getMessage());
        }
    }

    /**
     * 更新简历
     * PUT /api/resumes/{id}
     */
    @PutMapping("/{id}")
    public ApiResult<Resume> update(@PathVariable Long id, @RequestBody Resume resume) {
        try {
            Long userId = userService.getCurrentUserId();
            return ApiResult.success("简历更新成功", resumeService.update(id, resume, userId));
        } catch (RuntimeException e) {
            return ApiResult.badRequest(e.getMessage());
        }
    }

    /**
     * 删除简历
     * DELETE /api/resumes/{id}
     */
    @DeleteMapping("/{id}")
    public ApiResult<Void> delete(@PathVariable Long id) {
        try {
            Long userId = userService.getCurrentUserId();
            resumeService.delete(id, userId);
            return ApiResult.success("简历删除成功", null);
        } catch (RuntimeException e) {
            return ApiResult.badRequest(e.getMessage());
        }
    }
}
