package com.career.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.career.entity.InterviewRecord;
import org.apache.ibatis.annotations.Mapper;

/**
 * 面试记录 Mapper —— MyBatis Plus BaseMapper
 */
@Mapper
public interface InterviewRecordMapper extends BaseMapper<InterviewRecord> {
}
