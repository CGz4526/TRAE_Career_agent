package com.career.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.career.entity.JobDescription;
import com.career.mapper.JobDescriptionMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * 岗位描述服务 —— JD CRUD + 触发 AI 分析
 */
@Service
public class JobService {

    private static final Logger log = LoggerFactory.getLogger(JobService.class);

    private final JobDescriptionMapper jobDescriptionMapper;
    private final AiProxyService aiProxyService;

    public JobService(JobDescriptionMapper jobDescriptionMapper, AiProxyService aiProxyService) {
        this.jobDescriptionMapper = jobDescriptionMapper;
        this.aiProxyService = aiProxyService;
    }

    /**
     * 获取用户的所有岗位描述
     *
     * @param userId 用户 ID
     * @return 岗位描述列表
     */
    public List<JobDescription> listByUserId(Long userId) {
        return jobDescriptionMapper.selectList(
                new LambdaQueryWrapper<JobDescription>()
                        .eq(JobDescription::getUserId, userId)
                        .orderByDesc(JobDescription::getCreatedAt)
        );
    }

    /**
     * 根据 ID 获取岗位描述（验证归属权）
     *
     * @param id     JD ID
     * @param userId 用户 ID
     * @return 岗位描述实体
     */
    public JobDescription getById(Long id, Long userId) {
        JobDescription jd = jobDescriptionMapper.selectById(id);
        if (jd == null) {
            throw new RuntimeException("岗位描述不存在: " + id);
        }
        if (!jd.getUserId().equals(userId)) {
            throw new RuntimeException("无权访问该岗位描述");
        }
        return jd;
    }

    /**
     * 创建岗位描述
     *
     * @param jd 岗位描述实体（userId 已设置）
     * @return 创建后的岗位描述
     */
    public JobDescription create(JobDescription jd) {
        jobDescriptionMapper.insert(jd);
        log.info("岗位描述创建成功: {} (用户: {})", jd.getId(), jd.getUserId());
        return jd;
    }

    /**
     * 触发 AI 分析 —— 调用 Python AI 的岗位匹配 Agent
     *
     * @param id     JD ID
     * @param userId 用户 ID
     * @return 包含岗位画像的岗位描述
     */
    public JobDescription analyze(Long id, Long userId) {
        JobDescription jd = getById(id, userId);

        log.info("开始 AI 岗位分析, JD ID: {}", id);

        // 调用 Python AI 服务解析 JD
        Map<String, Object> jobProfile = aiProxyService.callMatchJob(jd.getRawText());

        // 更新岗位画像
        jd.setJobProfile(jobProfile);

        // 如果 AI 返回了岗位名称，更新岗位信息
        if (jobProfile != null && jobProfile.containsKey("position")) {
            String position = String.valueOf(jobProfile.get("position"));
            if (position != null && !position.isEmpty()) {
                jd.setPosition(position);
            }
        }

        jobDescriptionMapper.updateById(jd);
        log.info("AI 岗位分析完成, JD ID: {}", id);

        return jd;
    }
}
