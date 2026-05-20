package com.fitblocker.controller;

import com.fitblocker.dto.HistoryUpdateRequest;
import com.fitblocker.model.HabitTask;
import com.fitblocker.model.UserStats;
import com.fitblocker.repository.HabitTaskRepository;
import com.fitblocker.repository.UserStatsRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api")
public class ApiController {

    private final HabitTaskRepository taskRepository;
    private final UserStatsRepository statsRepository;

    public ApiController(HabitTaskRepository taskRepository, UserStatsRepository statsRepository) {
        this.taskRepository = taskRepository;
        this.statsRepository = statsRepository;
        initStats();
    }

    private void initStats() {
        if (statsRepository.findById(1L).isEmpty()) {
            statsRepository.save(new UserStats());
        }
    }

    @GetMapping("/stats")
    public UserStats getStats() {
        return statsRepository.findById(1L).orElse(new UserStats());
    }

    @GetMapping("/tasks")
    public List<HabitTask> getAllTasks() {
        return taskRepository.findAll();
    }

    @PostMapping("/tasks")
    public ResponseEntity<HabitTask> createTask(@RequestBody HabitTask task) {
        if (taskRepository.existsByName(task.getName())) {
            return ResponseEntity.badRequest().build();
        }
        return ResponseEntity.ok(taskRepository.save(task));
    }

    @PutMapping("/tasks/{id}/history")
    public ResponseEntity<Void> updateHistory(@PathVariable Long id, @RequestBody HistoryUpdateRequest request) {
        Optional<HabitTask> optionalTask = taskRepository.findById(id);

        if (optionalTask.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        HabitTask task = optionalTask.get();
        UserStats stats = statsRepository.findById(1L).get();

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
    public ResponseEntity<Void> deleteTask(@PathVariable Long id) {
        if (taskRepository.existsById(id)) {
            taskRepository.deleteById(id);
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.notFound().build();
    }
}