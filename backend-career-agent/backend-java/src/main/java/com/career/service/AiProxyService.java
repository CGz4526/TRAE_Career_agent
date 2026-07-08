package com.career.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * AI 代理服务 —— 代理调用 Python AI 服务
 */
@Service
public class AiProxyService {

    private static final Logger log = LoggerFactory.getLogger(AiProxyService.class);

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${ai-service.base-url}")
    private String baseUrl;

    @Value("${ai-service.endpoints.match-job}")
    private String matchJobEndpoint;

    @Value("${ai-service.endpoints.optimize-resume}")
    private String optimizeResumeEndpoint;

    @Value("${ai-service.endpoints.generate-questions}")
    private String generateQuestionsEndpoint;

    @Value("${ai-service.endpoints.project-story}")
    private String projectStoryEndpoint;

    @Value("${ai-service.endpoints.pipeline}")
    private String pipelineEndpoint;

    @Value("${ai-service.endpoints.interview-start}")
    private String interviewStartEndpoint;

    @Value("${ai-service.endpoints.interview-chat}")
    private String interviewChatEndpoint;

    @Value("${ai-service.endpoints.interview-report}")
    private String interviewReportEndpoint;

    public AiProxyService(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    // ==================== 核心 Agent 方法 ====================

    /**
     * 岗位匹配 Agent —— 解析 JD，返回结构化岗位需求画像
     *
     * @param jdText JD 原始文本
     * @return 岗位画像（Map）
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callMatchJob(String jdText) {
        log.info("调用岗位匹配 Agent, JD 文本长度: {}", jdText.length());
        Map<String, Object> request = new HashMap<>();
        request.put("jd_text", jdText);
        return postForObject(baseUrl + matchJobEndpoint, request);
    }

    /**
     * 简历优化 Agent —— 基于岗位画像优化简历
     *
     * @param resume     简历文本
     * @param jobProfile 岗位画像（JSON 字符串）
     * @return 优化结果（Map）
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callOptimizeResume(String resume, String jobProfile) {
        log.info("调用简历优化 Agent");
        Map<String, Object> jobProfileMap = parseJsonString(jobProfile);
        Map<String, Object> request = new HashMap<>();
        request.put("resume_text", resume);
        request.put("job_profile", jobProfileMap);
        return postForObject(baseUrl + optimizeResumeEndpoint, request);
    }

    /**
     * 简历优化 Agent（重载）—— 直接传入 Map
     *
     * @param resume     简历文本
     * @param jobProfile 岗位画像（Map）
     * @return 优化结果（Map）
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callOptimizeResume(String resume, Map<String, Object> jobProfile) {
        log.info("调用简历优化 Agent (Map 参数)");
        Map<String, Object> request = new HashMap<>();
        request.put("resume_text", resume);
        request.put("job_profile", jobProfile);
        return postForObject(baseUrl + optimizeResumeEndpoint, request);
    }

    /**
     * 题库生成 Agent —— 根据岗位画像生成面试题库
     *
     * @param jobProfile 岗位画像（JSON 字符串）
     * @return 题库（Map）
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callGenerateQuestions(String jobProfile) {
        log.info("调用题库生成 Agent");
        Map<String, Object> jobProfileMap = parseJsonString(jobProfile);
        Map<String, Object> request = new HashMap<>();
        request.put("job_profile", jobProfileMap);
        return postForObject(baseUrl + generateQuestionsEndpoint, request);
    }

    /**
     * 题库生成 Agent（重载）—— 直接传入 Map
     *
     * @param jobProfile 岗位画像（Map）
     * @return 题库（Map）
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callGenerateQuestions(Map<String, Object> jobProfile) {
        log.info("调用题库生成 Agent (Map 参数)");
        Map<String, Object> request = new HashMap<>();
        request.put("job_profile", jobProfile);
        return postForObject(baseUrl + generateQuestionsEndpoint, request);
    }

    /**
     * 项目梳理 Agent —— 用 STAR 法则梳理项目经历
     *
     * @param projectDesc 项目描述
     * @return 项目梳理结果（Map）
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callProjectStory(String projectDesc) {
        log.info("调用项目梳理 Agent");
        Map<String, Object> request = new HashMap<>();
        request.put("project_desc", projectDesc);
        return postForObject(baseUrl + projectStoryEndpoint, request);
    }

    /**
     * 多 Agent 全流程管线 —— JD解析 → 简历优化 + 题库生成 + 项目梳理
     *
     * @param jd          JD 文本
     * @param resume      简历文本（可为空）
     * @param projectDesc 项目描述（可为空）
     * @return 全流程结果（Map）
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callPipeline(String jd, String resume, String projectDesc) {
        log.info("调用全流程管线, JD 文本长度: {}", jd.length());
        Map<String, Object> request = new HashMap<>();
        request.put("jd_text", jd);
        request.put("resume_text", resume != null ? resume : "");
        request.put("project_desc", projectDesc != null ? projectDesc : "");
        return postForObject(baseUrl + pipelineEndpoint, request);
    }

    // ==================== 模拟面试 Agent 方法 ====================

    /**
     * 开始模拟面试
     *
     * @param jobProfile   岗位画像（Map）
     * @param questionBank 题库（可选）
     * @param resume       简历文本（可选）
     * @return 面试会话信息（Map）
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callInterviewStart(Map<String, Object> jobProfile,
                                                    Map<String, Object> questionBank,
                                                    String resume) {
        log.info("调用模拟面试启动 Agent");
        Map<String, Object> request = new HashMap<>();
        request.put("job_profile", jobProfile);
        if (questionBank != null) {
            request.put("question_bank", questionBank);
        }
        request.put("resume", resume != null ? resume : "");
        return postForObject(baseUrl + interviewStartEndpoint, request);
    }

    /**
     * 模拟面试对话
     *
     * @param sessionId 面试会话 ID
     * @param answer    候选人回答
     * @return 下一个问题（Map）
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callInterviewChat(String sessionId, String answer) {
        log.info("调用模拟面试对话 Agent, session: {}", sessionId);
        Map<String, Object> request = new HashMap<>();
        request.put("session_id", sessionId);
        request.put("answer", answer);
        return postForObject(baseUrl + interviewChatEndpoint, request);
    }

    /**
     * 获取面试评分报告
     *
     * @param sessionId 面试会话 ID
     * @return 评分报告（Map）
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> callInterviewReport(String sessionId) {
        log.info("获取面试评分报告, session: {}", sessionId);
        String url = baseUrl + interviewReportEndpoint.replace("{session_id}", sessionId);
        return getForObject(url);
    }

    // ==================== 内部工具方法 ====================

    /**
     * 发送 POST 请求
     */
    private Map<String, Object> postForObject(String url, Map<String, Object> requestBody) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            log.debug("AI 服务响应状态: {}", response.getStatusCode());
            return response.getBody();
        } catch (Exception e) {
            log.error("调用 AI 服务失败: {} - {}", url, e.getMessage());
            throw new RuntimeException("调用 AI 服务失败: " + e.getMessage(), e);
        }
    }

    /**
     * 发送 GET 请求
     */
    private Map<String, Object> getForObject(String url) {
        try {
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.GET, null, Map.class);
            log.debug("AI 服务响应状态: {}", response.getStatusCode());
            return response.getBody();
        } catch (Exception e) {
            log.error("调用 AI 服务失败: {} - {}", url, e.getMessage());
            throw new RuntimeException("调用 AI 服务失败: " + e.getMessage(), e);
        }
    }

    /**
     * 解析 JSON 字符串为 Map
     */
    private Map<String, Object> parseJsonString(String json) {
        if (json == null || json.isEmpty()) {
            return new HashMap<>();
        }
        try {
            return objectMapper.readValue(json, new TypeReference<Map<String, Object>>() {});
        } catch (Exception e) {
            log.error("JSON 解析失败: {}", e.getMessage());
            throw new RuntimeException("JSON 解析失败: " + e.getMessage(), e);
        }
    }
}
