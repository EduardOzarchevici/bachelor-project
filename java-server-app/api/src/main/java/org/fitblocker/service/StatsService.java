package org.fitblocker.service;

import org.fitblocker.model.AppUser;
import org.fitblocker.model.HabitTask;
import org.fitblocker.model.UserStats;
import org.fitblocker.repository.AppUserRepository;
import org.fitblocker.repository.HabitTaskRepository;
import org.fitblocker.repository.UserStatsRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class StatsService {

    private final UserStatsRepository statsRepository;
    private final HabitTaskRepository taskRepository;
    private final AppUserRepository userRepository;

    public StatsService(UserStatsRepository statsRepository, HabitTaskRepository taskRepository, AppUserRepository userRepository) {
        this.statsRepository = statsRepository;
        this.taskRepository = taskRepository;
        this.userRepository = userRepository;
    }

    private AppUser getAuthenticatedUser(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    @Transactional
    public UserStats getOrCreateStats(String username) {
        AppUser user = getAuthenticatedUser(username);
        return statsRepository.findByUser(user).orElseGet(() -> {
            UserStats newStats = new UserStats();
            newStats.setUser(user);
            return statsRepository.save(newStats);
        });
    }

    @Transactional
    public UserStats getUserStats(String username) {
        AppUser user = getAuthenticatedUser(username);
        UserStats stats = getOrCreateStats(username);

        List<HabitTask> tasks = taskRepository.findAllByUser(user);
        int completedDays = tasks.stream()
                .map(t -> t.getCompletedDates() == null ? 0 : t.getCompletedDates().size())
                .reduce(0, Integer::sum);

        stats.setXp(completedDays);

        if (stats.getPushupsTarget() <= 0) {
            stats.setPushupsTarget(5);
        }

        return statsRepository.save(stats);
    }
}