package org.fitblocker.controller;

import org.fitblocker.dto.HistoryUpdateRequest;
import org.fitblocker.model.HabitTask;
import org.fitblocker.model.UserStats;
import org.fitblocker.model.AppUser;
import org.fitblocker.repository.HabitTaskRepository;
import org.fitblocker.repository.UserStatsRepository;
import org.fitblocker.repository.AppUserRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api")
public class ApiController {

    private final HabitTaskRepository taskRepository;
    private final UserStatsRepository statsRepository;
    private final AppUserRepository userRepository;

    public ApiController(HabitTaskRepository taskRepository, UserStatsRepository statsRepository, AppUserRepository userRepository) {
        this.taskRepository = taskRepository;
        this.statsRepository = statsRepository;
        this.userRepository = userRepository;
    }

    private AppUser getAuthenticatedUser(Authentication authentication) {
        return userRepository.findByUsername(authentication.getName())
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    @GetMapping("/stats")
    public UserStats getStats(Authentication authentication) {
        AppUser user = getAuthenticatedUser(authentication);
        return statsRepository.findByUser(user).orElseGet(() -> {
            UserStats newStats = new UserStats();
            newStats.setUser(user);
            return statsRepository.save(newStats);
        });
    }

    @GetMapping("/tasks")
    public List<HabitTask> getAllTasks(Authentication authentication) {
        AppUser user = getAuthenticatedUser(authentication);
        return taskRepository.findAllByUser(user);
    }

    @PostMapping("/tasks")
    public ResponseEntity<HabitTask> createTask(@RequestBody HabitTask task, Authentication authentication) {
        AppUser user = getAuthenticatedUser(authentication);
        if (taskRepository.existsByNameAndUser(task.getName(), user)) {
            return ResponseEntity.badRequest().build();
        }
        task.setUser(user);
        return ResponseEntity.ok(taskRepository.save(task));
    }

    @PutMapping("/tasks/{id}/history")
    public ResponseEntity<Void> updateHistory(@PathVariable Long id, @RequestBody HistoryUpdateRequest request, Authentication authentication) {
        AppUser user = getAuthenticatedUser(authentication);
        Optional<HabitTask> optionalTask = taskRepository.findByIdAndUser(id, user);

        if (optionalTask.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        HabitTask task = optionalTask.get();
        UserStats stats = statsRepository.findByUser(user).orElseGet(() -> {
            UserStats newStats = new UserStats();
            newStats.setUser(user);
            return statsRepository.save(newStats);
        });

        if (request.isCompleted() && !task.getCompletedDates().contains(request.getDate())) {
            task.getCompletedDates().add(request.getDate());
            stats.setXp(stats.getXp() + 1);
        } else if (!request.isCompleted() && task.getCompletedDates().contains(request.getDate())) {
            task.getCompletedDates().remove(request.getDate());
            stats.setXp(Math.max(0, stats.getXp() - 1));
        }

        stats.setLevel((stats.getXp() / 10) + 1);

        taskRepository.save(task);
        statsRepository.save(stats);

        return ResponseEntity.ok().build();
    }

    @DeleteMapping("/tasks/{id}")
    public ResponseEntity<Void> deleteTask(@PathVariable Long id, Authentication authentication) {
        AppUser user = getAuthenticatedUser(authentication);
        Optional<HabitTask> optionalTask = taskRepository.findByIdAndUser(id, user);

        if (optionalTask.isPresent()) {
            taskRepository.delete(optionalTask.get());
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.notFound().build();
    }
}