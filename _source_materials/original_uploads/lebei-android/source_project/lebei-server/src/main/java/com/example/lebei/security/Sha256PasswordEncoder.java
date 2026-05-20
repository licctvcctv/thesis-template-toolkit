package com.example.lebei.security;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import org.springframework.stereotype.Component;

/**
 * Matches Android {@code PasswordUtils.encrypt}: SHA-256, lowercase hex.
 */
@Component
public class Sha256PasswordEncoder {

    public String encode(String rawPassword) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] bytes = digest.digest(rawPassword.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : bytes) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    sb.append('0');
                }
                sb.append(hex);
            }
            return sb.toString();
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    public boolean matches(String rawPassword, String encoded) {
        return encode(rawPassword).equalsIgnoreCase(encoded);
    }
}
