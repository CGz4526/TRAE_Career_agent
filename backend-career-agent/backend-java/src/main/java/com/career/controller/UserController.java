package com.career.controller;

import com.career.dto.ApiResult;
import com.career.dto.UpdateProfileRequest;
import com.career.dto.UserProfileResponse;
import com.career.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

/**
 * 用户资料控制器
 */
@RestController
@RequestMapping("/api/user")
public class UserController {

    private static final Logger log = LoggerFactory.getLogger(UserController.class);

    private final UserService userService;

    @Value("${app.upload-dir:uploads}")
    private String uploadDir;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    /**
     * 获取当前用户资料
     */
    @GetMapping("/profile")
    public ApiResult<UserProfileResponse> getProfile() {
        try {
            UserProfileResponse profile = userService.getCurrentProfile();
            return ApiResult.success(profile);
        } catch (RuntimeException e) {
            log.warn("获取用户资料失败: {}", e.getMessage());
            return ApiResult.badRequest(e.getMessage());
        }
    }

    /**
     * 更新用户资料
     */
    @PutMapping("/profile")
    public ApiResult<UserProfileResponse> updateProfile(@RequestBody UpdateProfileRequest request) {
        try {
            UserProfileResponse profile = userService.updateProfile(request);
            return ApiResult.success("更新成功", profile);
        } catch (RuntimeException e) {
            log.warn("更新用户资料失败: {}", e.getMessage());
            return ApiResult.badRequest(e.getMessage());
        }
    }

    /**
     * 检查昵称是否可用
     */
    @GetMapping("/check-nickname")
    public ApiResult<Boolean> checkNickname(@RequestParam String nickname) {
        boolean available = userService.checkNicknameAvailable(nickname);
        return ApiResult.success(available);
    }

    /**
     * 上传头像
     */
    @PostMapping("/avatar")
    public ApiResult<UserProfileResponse> uploadAvatar(@RequestParam("file") MultipartFile file) {
        try {
            if (file.isEmpty()) {
                return ApiResult.badRequest("请选择文件");
            }

            String originalFilename = file.getOriginalFilename();
            String ext = originalFilename != null && originalFilename.contains(".")
                    ? originalFilename.substring(originalFilename.lastIndexOf("."))
                    : ".png";

            if (!ext.matches("\\.(jpg|jpeg|png|gif|webp)$")) {
                return ApiResult.badRequest("仅支持 jpg/jpeg/png/gif/webp 格式");
            }

            if (file.getSize() > 5 * 1024 * 1024) {
                return ApiResult.badRequest("图片大小不能超过 5MB");
            }

            Path uploadPath = Paths.get(uploadDir, "avatars");
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            String filename = UUID.randomUUID().toString().replace("-", "") + ext;
            Path filePath = uploadPath.resolve(filename);
            file.transferTo(filePath.toFile());

            String avatarUrl = "/uploads/avatars/" + filename;
            UserProfileResponse profile = userService.updateAvatar(avatarUrl);
            log.info("头像上传成功: {}", avatarUrl);
            return ApiResult.success("上传成功", profile);
        } catch (IOException e) {
            log.error("头像上传失败", e);
            return ApiResult.badRequest("上传失败: " + e.getMessage());
        } catch (RuntimeException e) {
            log.warn("头像更新失败: {}", e.getMessage());
            return ApiResult.badRequest(e.getMessage());
        }
    }
}
