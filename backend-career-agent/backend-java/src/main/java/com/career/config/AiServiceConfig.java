package com.career.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.ClientHttpRequestFactory;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.reactive.function.client.WebClient;

/**
 * Python AI 服务调用配置 —— RestTemplate / WebClient Bean
 */
@Configuration
public class AiServiceConfig {

    @Value("${ai-service.base-url}")
    private String aiServiceBaseUrl;

    /**
     * RestTemplate Bean —— 用于同步调用 Python AI 服务
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate(clientHttpRequestFactory());
    }

    /**
     * WebClient Bean —— 用于响应式调用 Python AI 服务
     */
    @Bean
    public WebClient aiWebClient() {
        return WebClient.builder()
                .baseUrl(aiServiceBaseUrl)
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(16 * 1024 * 1024))
                .build();
    }

    /**
     * HTTP 请求工厂 —— 设置超时时间
     */
    private ClientHttpRequestFactory clientHttpRequestFactory() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        // 连接超时 10 秒
        factory.setConnectTimeout(10_000);
        // 读取超时 120 秒（AI 服务调用可能较慢）
        factory.setReadTimeout(120_000);
        return factory;
    }
}
