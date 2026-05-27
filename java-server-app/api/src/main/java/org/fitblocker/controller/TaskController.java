package org.fitblocker.controller;

import org.fitblocker.dto.HistoryUpdateRequest;
import org.fitblocker.model.HabitTask;
import org.fitblocker.security.UserPrincipal;
import org.fitblocker.service.TaskService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
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
    public ResponseEntity<List<HabitTask>> getAllTasks(@AuthenticationPrincipal UserPrincipal principal) {
        return ResponseEntity.ok(taskService.getAllTasks(principal.getId()));
    }

    @PostMapping
    public ResponseEntity<HabitTask> createTask(@RequestBody HabitTask task, @AuthenticationPrincipal UserPrincipal principal) {
        try {
            return ResponseEntity.ok(taskService.createTask(principal.getId(), task));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @PutMapping("/{id}/history")
    public ResponseEntity<Void> updateHistory(
            @PathVariable Long id,
            @RequestBody HistoryUpdateRequest request,
            @AuthenticationPrincipal UserPrincipal principal) {
        boolean updated = taskService.updateHistory(principal.getId(), id, request);
        return updated ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTask(@PathVariable Long id, @AuthenticationPrincipal UserPrincipal principal) {
        boolean deleted = taskService.deleteTask(principal.getId(), id);
        return deleted ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
    }
}