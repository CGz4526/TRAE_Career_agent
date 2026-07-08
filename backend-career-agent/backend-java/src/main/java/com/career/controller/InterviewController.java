package com.career.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.career.dto.ApiResult;
import com.career.entity.InterviewRecord;
import com.career.mapper.InterviewRecordMapper;
import com.career.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 面试记录控制器 —— 面试记录 CRUD
 */
@RestController
@RequestMapping("/api/interviews")
public class InterviewController {

    private static final Logger log = LoggerFactory.getLogger(InterviewController.class);

    private final InterviewRecordMapper interviewRecordMapper;
    private final UserService userService;

    public InterviewController(InterviewRecordMapper interviewRecordMapper, UserService userService) {
        this.interviewRecordMapper = interviewRecordMapper;
        this.userService = userService;
    }

    /**
     * 获取当前用户的所有面试记录
     * GET /api/interviews
     */
    @GetMapping
    public ApiResult<List<InterviewRecord>> list() {
        try {
            Long userId = userService.getCurrentUserId();
            List<InterviewRecord> records = interviewRecordMapper.selectList(
                    new LambdaQueryWrapper<InterviewRecord>()
                            .eq(InterviewRecord::getUserId, userId)
                            .orderByDesc(InterviewRecord::getStartedAt)
            );
            return ApiResult.success(records);
        } catch (RuntimeException e) {
            return ApiResult.serverError(e.getMessage());
        }
    }

    /**
     * 获取指定面试记录详情
     * GET /api/interviews/{id}
     */
    @GetMapping("/{id}")
    public ApiResult<InterviewRecord> getById(@PathVariable Long id) {
        try {
            Long userId = userService.getCurrentUserId();
            InterviewRecord record = interviewRecordMapper.selectById(id);
            if (record == null) {
                return ApiResult.badRequest("面试记录不存在: " + id);
            }
            if (!record.getUserId().equals(userId)) {
                return ApiResult.badRequest("无权访问该面试记录");
            }
            return ApiResult.success(record);
        } catch (RuntimeException e) {
            return ApiResult.serverError(e.getMessage());
        }
    }

    /**
     * 创建面试记录
     * POST /api/interviews
     */
    @PostMapping
    public ApiResult<InterviewRecord> create(@RequestBody InterviewRecord record) {
        try {
            Long userId = userService.getCurrentUserId();
            record.setUserId(userId);
            record.setStatus("pending");
            record.setStartedAt(LocalDateTime.now());
            interviewRecordMapper.insert(record);
            log.info("面试记录创建成功: {} (用户: {})", record.getId(), userId);
            return ApiResult.success("面试记录创建成功", record);
        } catch (RuntimeException e) {
            return ApiResult.serverError(e.getMessage());
        }
    }

    /**
     * 更新面试记录（更新对话消息或评分报告）
     * PUT /api/interviews/{id}
     */
    @PutMapping("/{id}")
    public ApiResult<InterviewRecord> update(@PathVariable Long id, @RequestBody InterviewRecord record) {
        try {
            Long userId = userService.getCurrentUserId();
            InterviewRecord existing = interviewRecordMapper.selectById(id);
            if (existing == null) {
                return ApiResult.badRequest("面试记录不存在: " + id);
            }
            if (!existing.getUserId().equals(userId)) {
                return ApiResult.badRequest("无权修改该面试记录");
            }

            record.setId(id);
            record.setUserId(userId);

            if (record.getMessages() != null) {
                existing.setMessages(record.getMessages());
            }
            if (record.getScoreReport() != null) {
                existing.setScoreReport(record.getScoreReport());
            }
            if (record.getStatus() != null) {
                existing.setStatus(record.getStatus());
            }
            if ("completed".equals(record.getStatus())) {
                existing.setEndedAt(LocalDateTime.now());
            }

            interviewRecordMapper.updateById(existing);
            return ApiResult.success("面试记录更新成功", existing);
        } catch (RuntimeException e) {
            return ApiResult.serverError(e.getMessage());
        }
    }
}
