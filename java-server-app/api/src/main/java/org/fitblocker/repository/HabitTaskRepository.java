package org.fitblocker.repository;


import org.fitblocker.model.HabitTask;
import org.fitblocker.model.AppUser;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface HabitTaskRepository extends JpaRepository<HabitTask, Long> {
    List<HabitTask> findAllByUser(AppUser user);
    Optional<HabitTask> findByIdAndUser(Long id, AppUser user);
    boolean existsByNameAndUser(String name, AppUser user);
}