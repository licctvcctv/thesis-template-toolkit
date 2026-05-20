package com.example.lebei.security;

import com.example.lebei.config.JwtProperties;
import com.example.lebei.entity.UserRole;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import javax.crypto.SecretKey;
import org.springframework.stereotype.Service;

@Service
public class JwtService {

    private static final String CLAIM_ROLE = "role";

    private final JwtProperties properties;
    private final SecretKey key;

    public JwtService(JwtProperties properties) {
        this.properties = properties;
        this.key = Keys.hmacShaKeyFor(properties.getSecret().getBytes(StandardCharsets.UTF_8));
    }

    public String generateToken(Long userId, String username, UserRole role) {
        long now = System.currentTimeMillis();
        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("username", username)
                .claim(CLAIM_ROLE, role.name())
                .issuedAt(new Date(now))
                .expiration(new Date(now + properties.getExpirationMs()))
                .signWith(key)
                .compact();
    }

    public Claims parse(String token) {
        return Jwts.parser().verifyWith(key).build().parseSignedClaims(token).getPayload();
    }

    public Long extractUserId(String token) {
        return Long.parseLong(parse(token).getSubject());
    }

    public UserRole extractRole(String token) {
        String r = parse(token).get(CLAIM_ROLE, String.class);
        if (r == null) {
            return UserRole.APP_USER;
        }
        return UserRole.valueOf(r);
    }
}
