package com.career.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.career.entity.Resume;
import org.apache.ibatis.annotations.Mapper;

/**
 * 简历 Mapper —— MyBatis Plus BaseMapper
 */
@Mapper
public interface ResumeMapper extends BaseMapper<Resume> {
}
