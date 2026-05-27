package org.fitblocker.controller;

import org.fitblocker.dto.HistoryUpdateRequest;
import org.fitblocker.model.HabitTask;
import org.fitblocker.service.TaskService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    @GetMapping
    public ResponseEntity<List<HabitTask>> getAllTasks(Authentication authentication) {
        return ResponseEntity.ok(taskService.getAllTasks(authentication.getName()));
    }

    @PostMapping
    public ResponseEntity<HabitTask> createTask(@RequestBody HabitTask task, Authentication authentication) {
        try {
            return ResponseEntity.ok(taskService.createTask(authentication.getName(), task));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @PutMapping("/{id}/history")
    public ResponseEntity<Void> updateHistory(
            @PathVariable Long id,
            @RequestBody HistoryUpdateRequest request,
            Authentication authentication) {
        boolean updated = taskService.updateHistory(authentication.getName(), id, request);
        return updated ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTask(@PathVariable Long id, Authentication authentication) {
        boolean deleted = taskService.deleteTask(authentication.getName(), id);
        return deleted ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
    }
}