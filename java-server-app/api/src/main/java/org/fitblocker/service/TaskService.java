package org.fitblocker.service;

import org.fitblocker.dto.HistoryUpdateRequest;
import org.fitblocker.model.AppUser;
import org.fitblocker.model.HabitTask;
import org.fitblocker.repository.AppUserRepository;
import org.fitblocker.repository.HabitTaskRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class TaskService {

    private final HabitTaskRepository taskRepository;
    private final AppUserRepository userRepository;

    public TaskService(HabitTaskRepository taskRepository, AppUserRepository userRepository) {
        this.taskRepository = taskRepository;
        this.userRepository = userRepository;
    }

    private AppUser getAuthenticatedUser(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    @Transactional(readOnly = true)
    public List<HabitTask> getAllTasks(String username) {
        AppUser user = getAuthenticatedUser(username);
        return taskRepository.findAllByUser(user);
    }

    @Transactional
    public HabitTask createTask(String username, HabitTask task) {
        AppUser user = getAuthenticatedUser(username);
        if (taskRepository.existsByNameAndUser(task.getName(), user)) {
            throw new IllegalArgumentException("Task already exists");
        }
        task.setUser(user);
        return taskRepository.save(task);
    }

    @Transactional
    public boolean updateHistory(String username, Long taskId, HistoryUpdateRequest request) {
        AppUser user = getAuthenticatedUser(username);
        Optional<HabitTask> optionalTask = taskRepository.findByIdAndUser(taskId, user);

        if (optionalTask.isEmpty()) {
            return false;
        }

        HabitTask task = optionalTask.get();

        if (request.isCompleted() && !task.getCompletedDates().contains(request.getDate())) {
            task.getCompletedDates().add(request.getDate());
        } else if (!request.isCompleted() && task.getCompletedDates().contains(request.getDate())) {
            task.getCompletedDates().remove(request.getDate());
        }

        taskRepository.save(task);
        return true;
    }

    @Transactional
    public boolean deleteTask(String username, Long taskId) {
        AppUser user = getAuthenticatedUser(username);
        Optional<HabitTask> optionalTask = taskRepository.findByIdAndUser(taskId, user);

        if (optionalTask.isPresent()) {
            taskRepository.delete(optionalTask.get());
            return true;
        }
        return false;
    }
}