package com.career.websocket;

import com.career.service.AiProxyService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 面试 WebSocket 处理器 —— 模拟面试实时通信
 *
 * 端点: /ws/interview
 *
 * 消息格式（客户端发送的 JSON）:
 * 1. 开始面试: { "action": "start", "job_profile": {...}, "question_bank": {...}, "resume": "..." }
 * 2. 发送回答: { "action": "chat", "session_id": "...", "answer": "..." }
 * 3. 获取报告: { "action": "report", "session_id": "..." }
 *
 * 服务端返回 AI 服务的原始 JSON 响应
 */
@Component
public class InterviewWebSocketHandler extends TextWebSocketHandler {

    private static final Logger log = LoggerFactory.getLogger(InterviewWebSocketHandler.class);

    private final ObjectMapper objectMapper;
    private final AiProxyService aiProxyService;

    /** WebSocket 会话 ID → AI 面试会话 ID 的映射 */
    private final ConcurrentHashMap<String, String> sessionAiMap = new ConcurrentHashMap<>();

    public InterviewWebSocketHandler(ObjectMapper objectMapper, AiProxyService aiProxyService) {
        this.objectMapper = objectMapper;
        this.aiProxyService = aiProxyService;
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        log.info("面试 WebSocket 连接建立: {}", session.getId());
        session.sendMessage(new TextMessage("{\"type\":\"connected\",\"message\":\"面试 WebSocket 已连接\"}"));
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        String payload = message.getPayload();
        log.debug("收到 WebSocket 消息: {}", payload);

        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> request = objectMapper.readValue(payload, Map.class);
            String action = (String) request.get("action");

            if (action == null) {
                sendError(session, "消息缺少 action 字段");
                return;
            }

            switch (action) {
                case "start":
                    handleStart(session, request);
                    break;
                case "chat":
                    handleChat(session, request);
                    break;
                case "report":
                    handleReport(session, request);
                    break;
                default:
                    sendError(session, "未知的 action: " + action);
            }
        } catch (Exception e) {
            log.error("处理 WebSocket 消息失败: {}", e.getMessage(), e);
            sendError(session, "处理消息失败: " + e.getMessage());
        }
    }

    /**
     * 处理开始面试
     */
    @SuppressWarnings("unchecked")
    private void handleStart(WebSocketSession session, Map<String, Object> request) throws IOException {
        try {
            Map<String, Object> jobProfile = (Map<String, Object>) request.get("job_profile");
            Map<String, Object> questionBank = (Map<String, Object>) request.get("question_bank");
            String resume = request.get("resume") != null ? String.valueOf(request.get("resume")) : "";

            if (jobProfile == null) {
                sendError(session, "缺少 job_profile 参数");
                return;
            }

            Map<String, Object> result = aiProxyService.callInterviewStart(jobProfile, questionBank, resume);

            // 保存 AI 会话 ID
            if (result != null && result.containsKey("session_id")) {
                String aiSessionId = String.valueOf(result.get("session_id"));
                sessionAiMap.put(session.getId(), aiSessionId);
            }

            sendResponse(session, result);
        } catch (Exception e) {
            log.error("开始面试失败: {}", e.getMessage(), e);
            sendError(session, "开始面试失败: " + e.getMessage());
        }
    }

    /**
     * 处理面试对话
     */
    private void handleChat(WebSocketSession session, Map<String, Object> request) throws IOException {
        try {
            String sessionId = request.get("session_id") != null
                    ? String.valueOf(request.get("session_id"))
                    : sessionAiMap.get(session.getId());

            if (sessionId == null) {
                sendError(session, "缺少 session_id，请先开始面试");
                return;
            }

            String answer = request.get("answer") != null ? String.valueOf(request.get("answer")) : "";
            Map<String, Object> result = aiProxyService.callInterviewChat(sessionId, answer);

            sendResponse(session, result);
        } catch (Exception e) {
            log.error("面试对话失败: {}", e.getMessage(), e);
            sendError(session, "面试对话失败: " + e.getMessage());
        }
    }

    /**
     * 处理获取评分报告
     */
    private void handleReport(WebSocketSession session, Map<String, Object> request) throws IOException {
        try {
            String sessionId = request.get("session_id") != null
                    ? String.valueOf(request.get("session_id"))
                    : sessionAiMap.get(session.getId());

            if (sessionId == null) {
                sendError(session, "缺少 session_id，请先开始面试");
                return;
            }

            Map<String, Object> result = aiProxyService.callInterviewReport(sessionId);

            sendResponse(session, result);
        } catch (Exception e) {
            log.error("获取评分报告失败: {}", e.getMessage(), e);
            sendError(session, "获取评分报告失败: " + e.getMessage());
        }
    }

    /**
     * 发送成功响应
     */
    private void sendResponse(WebSocketSession session, Map<String, Object> data) throws IOException {
        if (data == null) {
            data = new HashMap<>();
        }
        String json = objectMapper.writeValueAsString(data);
        session.sendMessage(new TextMessage(json));
    }

    /**
     * 发送错误消息
     */
    private void sendError(WebSocketSession session, String message) throws IOException {
        Map<String, Object> error = new HashMap<>();
        error.put("type", "error");
        error.put("message", message);
        String json = objectMapper.writeValueAsString(error);
        session.sendMessage(new TextMessage(json));
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        log.info("面试 WebSocket 连接关闭: {} (状态: {})", session.getId(), status);
        sessionAiMap.remove(session.getId());
    }

    @Override
    public void handleTransportError(WebSocketSession session, Throwable exception) throws Exception {
        log.error("面试 WebSocket 传输错误: {}", exception.getMessage(), exception);
        sessionAiMap.remove(session.getId());
    }
}
