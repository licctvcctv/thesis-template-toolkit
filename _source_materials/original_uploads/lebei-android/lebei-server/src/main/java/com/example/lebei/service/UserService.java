package com.example.lebei.service;

import com.example.lebei.dto.AuthResponse;
import com.example.lebei.dto.LearnedWordsSyncRequest;
import com.example.lebei.dto.LoginRequest;
import com.example.lebei.dto.PlanPatchRequest;
import com.example.lebei.dto.ProfileUpdateRequest;
import com.example.lebei.dto.RegisterRequest;
import com.example.lebei.dto.UserProfileDto;
import com.example.lebei.entity.UserEntity;
import com.example.lebei.entity.UserRole;
import com.example.lebei.repository.UserRepository;
import com.example.lebei.security.JwtService;
import com.example.lebei.security.Sha256PasswordEncoder;
import java.time.LocalDate;
import java.util.List;
import java.util.stream.IntStream;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final Sha256PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public UserService(UserRepository userRepository, Sha256PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    @Transactional
    public AuthResponse registerAppUser(RegisterRequest req) {
        if (userRepository.existsByUsername(req.getUsername())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "用户名已存在");
        }
        UserEntity u = new UserEntity();
        u.setUsername(req.getUsername());
        u.setPasswordHash(passwordEncoder.encode(req.getPassword()));
        u.setRole(UserRole.APP_USER);
        u.setProfileComplete(false);
        u.setDailyNewWords(10);
        u.setDailyReviewWords(20);
        u.setLearnedWordsCount(0);
        u.setMasteredWordsCount(0);
        u.setStudyPoints(0);
        u.setTodayLearnedCount(0);
        u.setTodayLearnedDate(null);
        userRepository.save(u);
        String token = jwtService.generateToken(u.getId(), u.getUsername(), UserRole.APP_USER);
        return new AuthResponse(token, UserMapper.toDto(u));
    }

    @Transactional(readOnly = true)
    public AuthResponse loginAppUser(LoginRequest req) {
        UserEntity u = userRepository
                .findByUsername(req.getUsername())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "用户名或密码错误"));
        if (u.getRole() != UserRole.APP_USER) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "请使用 App 端账号登录");
        }
        if (!passwordEncoder.matches(req.getPassword(), u.getPasswordHash())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "用户名或密码错误");
        }
        String token = jwtService.generateToken(u.getId(), u.getUsername(), UserRole.APP_USER);
        return new AuthResponse(token, UserMapper.toDto(u));
    }

    @Transactional(readOnly = true)
    public AuthResponse loginAdmin(LoginRequest req) {
        UserEntity u = userRepository
                .findByUsername(req.getUsername())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "用户名或密码错误"));
        if (u.getRole() != UserRole.ADMIN) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "非管理员账号");
        }
        if (!passwordEncoder.matches(req.getPassword(), u.getPasswordHash())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "用户名或密码错误");
        }
        String token = jwtService.generateToken(u.getId(), u.getUsername(), UserRole.ADMIN);
        return new AuthResponse(token, UserMapper.toDto(u));
    }

    @Transactional(readOnly = true)
    public UserProfileDto getProfile(Long userId) {
        return userRepository
                .findById(userId)
                .map(UserMapper::toDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
    }

    @Transactional
    public UserProfileDto updateProfile(Long userId, ProfileUpdateRequest req) {
        UserEntity u = requireAppUser(userId);
        u.setAgeGroup(req.getAgeGroup());
        u.setLevel(req.getLevel());
        u.setCurrentBookId(req.getCurrentBookId());
        u.setDailyNewWords(req.getDailyNewWords());
        u.setDailyReviewWords(req.getDailyReviewWords());
        u.setProfileComplete(req.getProfileComplete());
        userRepository.save(u);
        return UserMapper.toDto(u);
    }

    @Transactional
    public UserProfileDto updatePlan(Long userId, PlanPatchRequest req) {
        UserEntity u = requireAppUser(userId);
        u.setCurrentBookId(req.getCurrentBookId());
        u.setDailyNewWords(req.getDailyNewWords());
        u.setDailyReviewWords(req.getDailyReviewWords());
        userRepository.save(u);
        return UserMapper.toDto(u);
    }

    /** App 侧同步本地 Room 的学习统计，用于排行榜展示。 */
    @Transactional
    public UserProfileDto syncLearnedWords(Long userId, LearnedWordsSyncRequest req) {
        UserEntity u = requireAppUser(userId);
        int incoming = req.getLearnedWordsCount();
        int current = u.getLearnedWordsCount() == null ? 0 : u.getLearnedWordsCount();
        u.setLearnedWordsCount(Math.max(current, incoming));
        if (req.getMasteredWordsCount() != null) {
            u.setMasteredWordsCount(req.getMasteredWordsCount());
        }
        userRepository.save(u);
        return UserMapper.toDto(u);
    }

    /** App 每完成一个单词学习（点击简单/困难）调用一次：积分+1，当日计数累加（跨日重置）。 */
    @Transactional
    public UserProfileDto recordStudyWord(Long userId) {
        UserEntity u = requireAppUser(userId);
        String today = LocalDate.now().toString();
        if (u.getTodayLearnedDate() == null || !today.equals(u.getTodayLearnedDate())) {
            u.setTodayLearnedDate(today);
            u.setTodayLearnedCount(0);
        }
        int dayCnt = u.getTodayLearnedCount() == null ? 0 : u.getTodayLearnedCount();
        u.setTodayLearnedCount(dayCnt + 1);
        int pts = u.getStudyPoints() == null ? 0 : u.getStudyPoints();
        u.setStudyPoints(pts + 1);
        // 与积分一致：每完成一次学习（简单/困难）累计 +1，表示用户学习单词的总次数（含重复复习）
        int learned = u.getLearnedWordsCount() == null ? 0 : u.getLearnedWordsCount();
        u.setLearnedWordsCount(learned + 1);
        userRepository.save(u);
        return UserMapper.toDto(u);
    }

    private UserEntity requireAppUser(Long userId) {
        UserEntity u = userRepository.findById(userId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
        if (u.getRole() != UserRole.APP_USER) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN);
        }
        return u;
    }

    @Transactional(readOnly = true)
    public List<com.example.lebei.dto.LeaderboardEntryDto> leaderboardAppUsers(int limit) {
        return leaderboardForRole(UserRole.APP_USER, limit);
    }

    private List<com.example.lebei.dto.LeaderboardEntryDto> leaderboardForRole(UserRole role, int limit) {
        List<UserEntity> all = userRepository.findByRoleForLeaderboard(role);
        int cap = Math.min(Math.max(limit, 1), 200);
        return IntStream.range(0, Math.min(all.size(), cap))
                .mapToObj(
                        i -> {
                            UserEntity e = all.get(i);
                            return new com.example.lebei.dto.LeaderboardEntryDto(
                                    i + 1,
                                    e.getUsername(),
                                    e.getLearnedWordsCount() == null ? 0 : e.getLearnedWordsCount(),
                                    e.getMasteredWordsCount() == null ? 0 : e.getMasteredWordsCount(),
                                    e.getStudyPoints() == null ? 0 : e.getStudyPoints(),
                                    e.getTodayLearnedCount() == null ? 0 : e.getTodayLearnedCount());
                        })
                .toList();
    }
}
