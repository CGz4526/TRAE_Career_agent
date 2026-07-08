package com.career.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.career.entity.Resume;
import com.career.mapper.ResumeMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 简历服务 —— 简历 CRUD
 */
@Service
public class ResumeService {

    private static final Logger log = LoggerFactory.getLogger(ResumeService.class);

    private final ResumeMapper resumeMapper;

    public ResumeService(ResumeMapper resumeMapper) {
        this.resumeMapper = resumeMapper;
    }

    /**
     * 获取用户的所有简历
     *
     * @param userId 用户 ID
     * @return 简历列表
     */
    public List<Resume> listByUserId(Long userId) {
        return resumeMapper.selectList(
                new LambdaQueryWrapper<Resume>()
                        .eq(Resume::getUserId, userId)
                        .orderByDesc(Resume::getCreatedAt)
        );
    }

    /**
     * 根据 ID 获取简历（验证归属权）
     *
     * @param id     简历 ID
     * @param userId 用户 ID
     * @return 简历实体
     */
    public Resume getById(Long id, Long userId) {
        Resume resume = resumeMapper.selectById(id);
        if (resume == null) {
            throw new RuntimeException("简历不存在: " + id);
        }
        if (!resume.getUserId().equals(userId)) {
            throw new RuntimeException("无权访问该简历");
        }
        return resume;
    }

    /**
     * 创建简历
     *
     * @param resume 简历实体（userId 已设置）
     * @return 创建后的简历（包含 ID）
     */
    public Resume create(Resume resume) {
        if (resume.getStatus() == null) {
            resume.setStatus("draft");
        }
        resumeMapper.insert(resume);
        log.info("简历创建成功: {} (用户: {})", resume.getId(), resume.getUserId());
        return resume;
    }

    /**
     * 更新简历
     *
     * @param id     简历 ID
     * @param resume 更新内容
     * @param userId 用户 ID
     * @return 更新后的简历
     */
    public Resume update(Long id, Resume resume, Long userId) {
        Resume existing = getById(id, userId);
        resume.setId(id);
        resume.setUserId(userId);

        // 只更新非空字段
        if (resume.getTitle() != null) {
            existing.setTitle(resume.getTitle());
        }
        if (resume.getContent() != null) {
            existing.setContent(resume.getContent());
        }
        if (resume.getOptimizedContent() != null) {
            existing.setOptimizedContent(resume.getOptimizedContent());
        }
        if (resume.getStatus() != null) {
            existing.setStatus(resume.getStatus());
        }

        resumeMapper.updateById(existing);
        log.info("简历更新成功: {}", id);
        return existing;
    }

    /**
     * 删除简历
     *
     * @param id     简历 ID
     * @param userId 用户 ID
     */
    public void delete(Long id, Long userId) {
        getById(id, userId); // 验证归属权
        resumeMapper.deleteById(id);
        log.info("简历删除成功: {}", id);
    }
}
