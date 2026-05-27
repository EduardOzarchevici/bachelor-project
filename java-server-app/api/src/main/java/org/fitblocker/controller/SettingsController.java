package org.fitblocker.controller;

import org.fitblocker.dto.PushupsSettingsRequest;
import org.fitblocker.dto.PushupsSettingsResponse;
import org.fitblocker.model.AppUser;
import org.fitblocker.model.UserStats;
import org.fitblocker.repository.AppUserRepository;
import org.fitblocker.repository.UserStatsRepository;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/settings")
public class SettingsController {

    private final UserStatsRepository statsRepository;
    private final AppUserRepository userRepository;

    public SettingsController(UserStatsRepository statsRepository, AppUserRepository userRepository) {
        this.statsRepository = statsRepository;
        this.userRepository = userRepository;
    }

    private AppUser getAuthenticatedUser(Authentication authentication) {
        return userRepository.findByUsername(authentication.getName())
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    private UserStats getOrCreateStats(AppUser user) {
        return statsRepository.findByUser(user).orElseGet(() -> {
            UserStats newStats = new UserStats();
            newStats.setUser(user);
            // pushupsTarget will default to 5 via field initializer
            return statsRepository.save(newStats);
        });
    }

    @GetMapping("/pushups")
    public PushupsSettingsResponse getPushupsTarget(Authentication authentication) {
        AppUser user = getAuthenticatedUser(authentication);
        UserStats stats = getOrCreateStats(user);

        return new PushupsSettingsResponse(stats.getPushupsTarget());
    }

    @PutMapping("/pushups")
    public PushupsSettingsResponse updatePushupsTarget(
            @RequestBody PushupsSettingsRequest request,
            Authentication authentication
    ) {
        AppUser user = getAuthenticatedUser(authentication);
        UserStats stats = getOrCreateStats(user);

        int target = request.getPushupsTarget();
        if (target < 1) {
            target = 1;
        }
        if (target > 500) {
            target = 500;
        }

        stats.setPushupsTarget(target);
        statsRepository.save(stats);

        return new PushupsSettingsResponse(stats.getPushupsTarget());
    }
}

