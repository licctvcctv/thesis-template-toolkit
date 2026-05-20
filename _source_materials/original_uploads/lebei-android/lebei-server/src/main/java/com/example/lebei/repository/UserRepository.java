package com.example.lebei.repository;

import com.example.lebei.entity.UserEntity;
import com.example.lebei.entity.UserRole;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface UserRepository extends JpaRepository<UserEntity, Long> {

    Optional<UserEntity> findByUsername(String username);

    boolean existsByUsername(String username);

    long countByRole(UserRole role);

    @Query(
            "SELECT u FROM UserEntity u WHERE u.role = :role ORDER BY u.studyPoints DESC, u.learnedWordsCount DESC, u.username ASC")
    List<UserEntity> findByRoleForLeaderboard(@Param("role") UserRole role);
}
