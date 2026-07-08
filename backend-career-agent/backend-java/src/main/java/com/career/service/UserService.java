package com.career.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.career.dto.JwtResponse;
import com.career.dto.LoginRequest;
import com.career.dto.RegisterRequest;
import com.career.dto.UpdateProfileRequest;
import com.career.dto.UserProfileResponse;
import com.career.entity.User;
import com.career.mapper.UserMapper;
import com.career.security.JwtUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * 用户服务 —— 注册/登录
 */
@Service
public class UserService {

    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final AuthenticationManager authenticationManager;

    public UserService(UserMapper userMapper,
                       PasswordEncoder passwordEncoder,
                       JwtUtil jwtUtil,
                       AuthenticationManager authenticationManager) {
        this.userMapper = userMapper;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
        this.authenticationManager = authenticationManager;
    }

    /**
     * 用户注册
     *
     * @param request 注册请求
     * @return JWT 响应（注册后自动登录）
     */
    public JwtResponse register(RegisterRequest request) {
        // 检查用户名是否已存在
        Long existingCount = userMapper.selectCount(
                new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername())
        );
        if (existingCount > 0) {
            throw new RuntimeException("用户名已存在: " + request.getUsername());
        }

        // 创建用户
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPasswordHash(passwordEncoder.encode(request.getPassword()));
        user.setEmail(request.getEmail() != null ? request.getEmail() : "");
        user.setTechStack(request.getTechStack() != null ? request.getTechStack() : "");

        userMapper.insert(user);
        log.info("用户注册成功: {} (ID: {})", user.getUsername(), user.getId());

        // 生成 JWT Token
        String token = jwtUtil.generateToken(user.getId(), user.getUsername());

        return JwtResponse.builder()
                .token(token)
                .type("Bearer")
                .username(user.getUsername())
                .userId(user.getId())
                .build();
    }

    /**
     * 用户登录
     *
     * @param request 登录请求
     * @return JWT 响应
     */
    public JwtResponse login(LoginRequest request) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
            );

            SecurityContextHolder.getContext().setAuthentication(authentication);

            User user = userMapper.selectOne(
                    new LambdaQueryWrapper<User>().eq(User::getUsername, request.getUsername())
            );

            String token = jwtUtil.generateToken(user.getId(), user.getUsername());
            log.info("用户登录成功: {} (ID: {})", user.getUsername(), user.getId());

            return JwtResponse.builder()
                    .token(token)
                    .type("Bearer")
                    .username(user.getUsername())
                    .userId(user.getId())
                    .build();
        } catch (BadCredentialsException e) {
            throw new RuntimeException("用户名或密码错误");
        }
    }

    /**
     * 获取当前登录用户 ID
     *
     * @return 当前用户 ID
     */
    public Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new RuntimeException("用户未认证");
        }

        String username = authentication.getName();
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>().eq(User::getUsername, username)
        );

        if (user == null) {
            throw new RuntimeException("用户不存在: " + username);
        }

        return user.getId();
    }

    /**
     * 根据用户名获取用户信息
     *
     * @param username 用户名
     * @return 用户实体
     */
    public User findByUsername(String username) {
        return userMapper.selectOne(
                new LambdaQueryWrapper<User>().eq(User::getUsername, username)
        );
    }

    /**
     * 根据 ID 获取用户信息
     *
     * @param userId 用户 ID
     * @return 用户实体
     */
    public User findById(Long userId) {
        return userMapper.selectById(userId);
    }

    public UserProfileResponse getCurrentProfile() {
        Long userId = getCurrentUserId();
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        return toProfileResponse(user);
    }

    public UserProfileResponse updateProfile(UpdateProfileRequest request) {
        Long userId = getCurrentUserId();
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        if (request.getNickname() != null && !request.getNickname().isEmpty()) {
            Long count = userMapper.selectCount(
                    new LambdaQueryWrapper<User>()
                            .eq(User::getNickname, request.getNickname())
                            .ne(User::getId, userId)
            );
            if (count > 0) {
                throw new RuntimeException("昵称已被使用，请换一个");
            }
            user.setNickname(request.getNickname());
        }

        userMapper.updateById(user);
        log.info("用户资料更新成功: {} (ID: {})", user.getUsername(), user.getId());
        return toProfileResponse(user);
    }

    public UserProfileResponse updateAvatar(String avatarUrl) {
        Long userId = getCurrentUserId();
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        user.setAvatar(avatarUrl);
        userMapper.updateById(user);
        log.info("用户头像更新成功: {} (ID: {})", user.getUsername(), user.getId());
        return toProfileResponse(user);
    }

    public boolean checkNicknameAvailable(String nickname) {
        Long userId;
        try {
            userId = getCurrentUserId();
        } catch (RuntimeException e) {
            userId = null;
        }

        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<User>()
                .eq(User::getNickname, nickname);
        if (userId != null) {
            wrapper.ne(User::getId, userId);
        }
        Long count = userMapper.selectCount(wrapper);
        return count == 0;
    }

    private UserProfileResponse toProfileResponse(User user) {
        return UserProfileResponse.builder()
                .userId(user.getId())
                .username(user.getUsername())
                .nickname(user.getNickname() != null ? user.getNickname() : user.getUsername())
                .avatar(user.getAvatar())
                .email(user.getEmail())
                .techStack(user.getTechStack())
                .createdAt(user.getCreatedAt())
                .build();
    }
}
