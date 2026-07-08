package com.career.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.career.entity.User;
import org.apache.ibatis.annotations.Mapper;

/**
 * 用户 Mapper —— MyBatis Plus BaseMapper
 */
@Mapper
public interface UserMapper extends BaseMapper<User> {
}
