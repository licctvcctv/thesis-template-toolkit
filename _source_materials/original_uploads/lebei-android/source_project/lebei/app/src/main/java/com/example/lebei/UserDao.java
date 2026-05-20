package com.example.lebei;

import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.Query;
import androidx.room.Update;

@Dao
public interface UserDao {
    @Insert
    void insert(User user);

    @Query("SELECT * FROM user WHERE username = :username LIMIT 1")
    User getUserByUsername(String username);

    @Update
    void update(User user);  // 新增加的方法
}