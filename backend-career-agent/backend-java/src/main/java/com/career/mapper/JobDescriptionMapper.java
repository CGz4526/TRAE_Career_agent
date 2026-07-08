package com.career.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.career.entity.JobDescription;
import org.apache.ibatis.annotations.Mapper;

/**
 * 岗位描述 Mapper —— MyBatis Plus BaseMapper
 */
@Mapper
public interface JobDescriptionMapper extends BaseMapper<JobDescription> {
}
