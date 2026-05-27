package org.fitblocker.service;

import org.fitblocker.dto.PushupsSettingsRequest;
import org.fitblocker.dto.PushupsSettingsResponse;
import org.fitblocker.model.AppUser;
import org.fitblocker.model.UserStats;
import org.fitblocker.repository.AppUserRepository;
import org.fitblocker.repository.UserStatsRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class SettingsService {

    private final UserStatsRepository statsRepository;
    private final AppUserRepository userRepository;

    public SettingsService(UserStatsRepository statsRepository, AppUserRepository userRepository) {
        this.statsRepository = statsRepository;
        this.userRepository = userRepository;
    }

    private AppUser getAuthenticatedUser(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    @Transactional
    public UserStats getOrCreateStats(Long userId) {
        AppUser user = getAuthenticatedUser(userId);
        return statsRepository.findByUser(user).orElseGet(() -> {
            UserStats newStats = new UserStats();
            newStats.setUser(user);
            return statsRepository.save(newStats);
        });
    }

    @Transactional(readOnly = true)
    public PushupsSettingsResponse getPushupsTarget(Long userId) {
        AppUser user = getAuthenticatedUser(userId);
        UserStats stats = statsRepository.findByUser(user).orElseGet(() -> getOrCreateStats(userId));
        return new PushupsSettingsResponse(stats.getPushupsTarget());
    }

    @Transactional
    public PushupsSettingsResponse updatePushupsTarget(Long userId, PushupsSettingsRequest request) {
        UserStats stats = getOrCreateStats(userId);
        int target = request.getPushupsTarget();

        if (target < 1) {
            target = 1;
        } else if (target > 500) {
            target = 500;
        }

        stats.setPushupsTarget(target);
        statsRepository.save(stats);

        return new PushupsSettingsResponse(stats.getPushupsTarget());
    }
}