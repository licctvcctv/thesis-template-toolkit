package com.example.lebei.config;

import com.example.lebei.entity.UserEntity;
import com.example.lebei.entity.UserRole;
import com.example.lebei.repository.UserRepository;
import com.example.lebei.security.Sha256PasswordEncoder;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
public class AdminBootstrapRunner implements ApplicationRunner {

    private final UserRepository userRepository;
    private final Sha256PasswordEncoder passwordEncoder;
    private final AdminBootstrapProperties adminProps;

    public AdminBootstrapRunner(
            UserRepository userRepository,
            Sha256PasswordEncoder passwordEncoder,
            AdminBootstrapProperties adminProps) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.adminProps = adminProps;
    }

    @Override
    public void run(ApplicationArguments args) {
        if (userRepository.countByRole(UserRole.ADMIN) > 0) {
            return;
        }
        String un = adminProps.getUsername() != null ? adminProps.getUsername().trim() : "admin";
        if (un.isEmpty()) {
            un = "admin";
        }
        if (userRepository.existsByUsername(un)) {
            return;
        }
        UserEntity admin = new UserEntity();
        admin.setUsername(un);
        admin.setPasswordHash(passwordEncoder.encode(adminProps.getInitialPassword()));
        admin.setRole(UserRole.ADMIN);
        admin.setProfileComplete(true);
        admin.setDailyNewWords(0);
        admin.setDailyReviewWords(0);
        admin.setLearnedWordsCount(0);
        admin.setMasteredWordsCount(0);
        userRepository.save(admin);
    }
}
