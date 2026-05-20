package com.example.lebei.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "users")
public class UserEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 32)
    private String username;

    @Column(name = "password_hash", nullable = false, length = 128)
    private String passwordHash;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 16)
    private UserRole role = UserRole.APP_USER;

    @Column(name = "age_group")
    private Integer ageGroup;

    @Column(length = 16)
    private String level;

    @Column(name = "current_book_id", length = 32)
    private String currentBookId;

    @Column(name = "is_profile_complete")
    private Boolean profileComplete = false;

    @Column(name = "daily_new_words")
    private Integer dailyNewWords = 10;

    @Column(name = "daily_review_words")
    private Integer dailyReviewWords = 20;

    @Column(name = "learned_words_count", nullable = false)
    private Integer learnedWordsCount = 0;

    /** App 本地按权重 > 5 统计的已掌握词汇数 */
    @Column(name = "mastered_words_count", nullable = false)
    private Integer masteredWordsCount = 0;

    /** 每完成一次学习（App 点击简单/困难）+1，用于排行榜积分 */
    @Column(name = "study_points", nullable = false)
    private Integer studyPoints = 0;

    /** 自然日（服务器本地日期）内已完成学习的次数，跨日重置 */
    @Column(name = "today_learned_count", nullable = false)
    private Integer todayLearnedCount = 0;

    @Column(name = "today_learned_date", length = 10)
    private String todayLearnedDate;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPasswordHash() {
        return passwordHash;
    }

    public void setPasswordHash(String passwordHash) {
        this.passwordHash = passwordHash;
    }

    public UserRole getRole() {
        return role;
    }

    public void setRole(UserRole role) {
        this.role = role;
    }

    public Integer getAgeGroup() {
        return ageGroup;
    }

    public void setAgeGroup(Integer ageGroup) {
        this.ageGroup = ageGroup;
    }

    public String getLevel() {
        return level;
    }

    public void setLevel(String level) {
        this.level = level;
    }

    public String getCurrentBookId() {
        return currentBookId;
    }

    public void setCurrentBookId(String currentBookId) {
        this.currentBookId = currentBookId;
    }

    public Boolean getProfileComplete() {
        return profileComplete;
    }

    public void setProfileComplete(Boolean profileComplete) {
        this.profileComplete = profileComplete;
    }

    public Integer getDailyNewWords() {
        return dailyNewWords;
    }

    public void setDailyNewWords(Integer dailyNewWords) {
        this.dailyNewWords = dailyNewWords;
    }

    public Integer getDailyReviewWords() {
        return dailyReviewWords;
    }

    public void setDailyReviewWords(Integer dailyReviewWords) {
        this.dailyReviewWords = dailyReviewWords;
    }

    public Integer getLearnedWordsCount() {
        return learnedWordsCount;
    }

    public void setLearnedWordsCount(Integer learnedWordsCount) {
        this.learnedWordsCount = learnedWordsCount;
    }

    public Integer getMasteredWordsCount() {
        return masteredWordsCount;
    }

    public void setMasteredWordsCount(Integer masteredWordsCount) {
        this.masteredWordsCount = masteredWordsCount;
    }

    public Integer getStudyPoints() {
        return studyPoints;
    }

    public void setStudyPoints(Integer studyPoints) {
        this.studyPoints = studyPoints;
    }

    public Integer getTodayLearnedCount() {
        return todayLearnedCount;
    }

    public void setTodayLearnedCount(Integer todayLearnedCount) {
        this.todayLearnedCount = todayLearnedCount;
    }

    public String getTodayLearnedDate() {
        return todayLearnedDate;
    }

    public void setTodayLearnedDate(String todayLearnedDate) {
        this.todayLearnedDate = todayLearnedDate;
    }
}
