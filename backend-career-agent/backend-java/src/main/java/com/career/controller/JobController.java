package com.career.controller;

import com.career.dto.ApiResult;
import com.career.entity.JobDescription;
import com.career.service.JobService;
import com.career.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 岗位描述控制器 —— JD CRUD + 触发 AI 分析
 */
@RestController
@RequestMapping("/api/jobs")
public class JobController {

    private static final Logger log = LoggerFactory.getLogger(JobController.class);

    private final JobService jobService;
    private final UserService userService;

    public JobController(JobService jobService, UserService userService) {
        this.jobService = jobService;
        this.userService = userService;
    }

    /**
     * 获取当前用户的所有岗位描述
     * GET /api/jobs
     */
    @GetMapping
    public ApiResult<List<JobDescription>> list() {
        try {
            Long userId = userService.getCurrentUserId();
            return ApiResult.success(jobService.listByUserId(userId));
        } catch (RuntimeException e) {
            return ApiResult.serverError(e.getMessage());
        }
    }

    /**
     * 获取指定岗位描述详情
     * GET /api/jobs/{id}
     */
    @GetMapping("/{id}")
    public ApiResult<JobDescription> getById(@PathVariable Long id) {
        try {
            Long userId = userService.getCurrentUserId();
            return ApiResult.success(jobService.getById(id, userId));
        } catch (RuntimeException e) {
            return ApiResult.badRequest(e.getMessage());
        }
    }

    /**
     * 创建岗位描述
     * POST /api/jobs
     */
    @PostMapping
    public ApiResult<JobDescription> create(@RequestBody JobDescription jd) {
        try {
            Long userId = userService.getCurrentUserId();
            jd.setUserId(userId);
            return ApiResult.success("岗位描述创建成功", jobService.create(jd));
        } catch (RuntimeException e) {
            return ApiResult.serverError(e.getMessage());
        }
    }

    /**
     * 触发 AI 岗位分析（调用 Python AI 的 /agent/match-job）
     * POST /api/jobs/{id}/analyze
     */
    @PostMapping("/{id}/analyze")
    public ApiResult<JobDescription> analyze(@PathVariable Long id) {
        try {
            Long userId = userService.getCurrentUserId();
            JobDescription result = jobService.analyze(id, userId);
            return ApiResult.success("AI 岗位分析完成", result);
        } catch (RuntimeException e) {
            log.error("AI 岗位分析失败: {}", e.getMessage());
            return ApiResult.error(500, "AI 岗位分析失败: " + e.getMessage());
        }
    }
}
