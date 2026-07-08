package com.career.config;

import com.career.security.JwtAuthenticationFilter;
import com.career.security.JwtUtil;
import com.career.security.UserDetailsServiceImpl;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.http.HttpStatus;

/**
 * Spring Security 配置 —— JWT 无状态认证
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtUtil jwtUtil;
    private final UserDetailsServiceImpl userDetailsService;
    private final CorsConfigurationSource corsConfigurationSource;

    public SecurityConfig(JwtUtil jwtUtil,
                          UserDetailsServiceImpl userDetailsService,
                          CorsConfigurationSource corsConfigurationSource) {
        this.jwtUtil = jwtUtil;
        this.userDetailsService = userDetailsService;
        this.corsConfigurationSource = corsConfigurationSource;
    }

    /**
     * 密码编码器 —— BCrypt
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    /**
     * 认证提供者
     */
    @Bean
    public DaoAuthenticationProvider authenticationProvider() {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userDetailsService);
        provider.setPasswordEncoder(passwordEncoder());
        return provider;
    }

    /**
     * 认证管理器
     */
    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    /**
     * 安全过滤器链
     */
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // 启用 CORS（使用 CorsConfig 中的配置）
            .cors(cors -> cors.configurationSource(corsConfigurationSource))
            // 禁用 CSRF（JWT 无状态不需要）
            .csrf(AbstractHttpConfigurer::disable)
            // 无状态会话
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            // 路径权限配置
            .authorizeHttpRequests(auth -> auth
                // 认证相关路径不需要认证
                .requestMatchers("/api/auth/**").permitAll()
                // 检查昵称可用性（注册/编辑时调用，无需认证）
                .requestMatchers("/api/user/check-nickname").permitAll()
                // WebSocket 端点不需要认证（通过 token 参数认证）
                .requestMatchers("/ws/**").permitAll()
                // 健康检查不需要认证
                .requestMatchers("/actuator/**", "/health").permitAll()
                // 静态资源
                .requestMatchers("/uploads/**").permitAll()
                // 其他所有路径需要认证
                .anyRequest().authenticated()
            )
            // 未认证时返回 401 而不是 403
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint((request, response, authException) -> {
                    response.setStatus(HttpStatus.UNAUTHORIZED.value());
                    response.setContentType("application/json;charset=UTF-8");
                    response.getWriter().write("{\"code\":401,\"message\":\"未登录或登录已过期\",\"data\":null}");
                })
            )
            // 认证提供者
            .authenticationProvider(authenticationProvider())
            // 添加 JWT 过滤器（手动创建实例，避免被自动注册为 Servlet Filter）
            .addFilterBefore(
                    new JwtAuthenticationFilter(jwtUtil, userDetailsService),
                    UsernamePasswordAuthenticationFilter.class
            );

        return http.build();
    }
}
