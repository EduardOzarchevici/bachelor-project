//package org.fitblocker.controller;
//
//import org.fitblocker.dto.HistoryUpdateRequest;
//import org.fitblocker.model.HabitTask;
//import org.fitblocker.model.UserStats;
//import org.fitblocker.model.AppUser;
//import org.fitblocker.repository.HabitTaskRepository;
//import org.fitblocker.repository.UserStatsRepository;
//import org.fitblocker.repository.AppUserRepository;
//import org.springframework.http.ResponseEntity;
//import org.springframework.security.core.Authentication;
//import org.springframework.web.bind.annotation.*;
//
//import java.util.List;
//import java.util.Optional;
//
//@RestController
//@RequestMapping("/api")
//public class ApiController {
//
//    private final HabitTaskRepository taskRepository;
//    private final UserStatsRepository statsRepository;
//    private final AppUserRepository userRepository;
//
//    public ApiController(HabitTaskRepository taskRepository, UserStatsRepository statsRepository, AppUserRepository userRepository) {
//        this.taskRepository = taskRepository;
//        this.statsRepository = statsRepository;
//        this.userRepository = userRepository;
//    }
//
//    private AppUser getAuthenticatedUser(Authentication authentication) {
//        return userRepository.findByUsername(authentication.getName())
//                .orElseThrow(() -> new RuntimeException("User not found"));
//    }
//
//    @GetMapping("/stats")
//    public UserStats getStats(Authentication authentication) {
//        AppUser user = getAuthenticatedUser(authentication);
//        UserStats stats = statsRepository.findByUser(user).orElseGet(() -> {
//            UserStats newStats = new UserStats();
//            newStats.setUser(user);
//            return statsRepository.save(newStats);
//        });
//
//        // XP is always computed as "sum of all completed task days"
//        List<HabitTask> tasks = taskRepository.findAllByUser(user);
//        int completedDays = tasks.stream()
//                .map(t -> t.getCompletedDates() == null ? 0 : t.getCompletedDates().size())
//                .reduce(0, Integer::sum);
//        stats.setXp(completedDays);
//
//        // Backward-compatible default if an older row exists with an unset value.
//        if (stats.getPushupsTarget() <= 0) {
//            stats.setPushupsTarget(5);
//        }
//
//        return statsRepository.save(stats);
//    }
//
//    @GetMapping("/tasks")
//    public List<HabitTask> getAllTasks(Authentication authentication) {
//        AppUser user = getAuthenticatedUser(authentication);
//        return taskRepository.findAllByUser(user);
//    }
//
//    @PostMapping("/tasks")
//    public ResponseEntity<HabitTask> createTask(@RequestBody HabitTask task, Authentication authentication) {
//        AppUser user = getAuthenticatedUser(authentication);
//        if (taskRepository.existsByNameAndUser(task.getName(), user)) {
//            return ResponseEntity.badRequest().build();
//        }
//        task.setUser(user);
//        return ResponseEntity.ok(taskRepository.save(task));
//    }
//
//    @PutMapping("/tasks/{id}/history")
//    public ResponseEntity<Void> updateHistory(@PathVariable Long id, @RequestBody HistoryUpdateRequest request, Authentication authentication) {
//        AppUser user = getAuthenticatedUser(authentication);
//        Optional<HabitTask> optionalTask = taskRepository.findByIdAndUser(id, user);
//
//        if (optionalTask.isEmpty()) {
//            return ResponseEntity.notFound().build();
//        }
//
//        HabitTask task = optionalTask.get();
//
//        if (request.isCompleted() && !task.getCompletedDates().contains(request.getDate())) {
//            task.getCompletedDates().add(request.getDate());
//        } else if (!request.isCompleted() && task.getCompletedDates().contains(request.getDate())) {
//            task.getCompletedDates().remove(request.getDate());
//        }
//
//        taskRepository.save(task);
//
//        return ResponseEntity.ok().build();
//    }
//
//    @DeleteMapping("/tasks/{id}")
//    public ResponseEntity<Void> deleteTask(@PathVariable Long id, Authentication authentication) {
//        AppUser user = getAuthenticatedUser(authentication);
//        Optional<HabitTask> optionalTask = taskRepository.findByIdAndUser(id, user);
//
//        if (optionalTask.isPresent()) {
//            taskRepository.delete(optionalTask.get());
//            return ResponseEntity.ok().build();
//        }
//        return ResponseEntity.notFound().build();
//    }
//}