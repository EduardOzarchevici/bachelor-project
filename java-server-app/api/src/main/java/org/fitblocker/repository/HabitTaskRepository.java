package com.fitblocker.repository;

import com.fitblocker.model.HabitTask;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface HabitTaskRepository extends JpaRepository<HabitTask, Long> {
    boolean existsByName(String name);
}