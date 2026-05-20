package com.fitblocker.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "user_stats")
public class UserStats {
    @Id
    private Long id = 1L;
    private int xp = 0;
    private int level = 1;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public int getXp() { return xp; }
    public void setXp(int xp) { this.xp = xp; }
    public int getLevel() { return level; }
    public void setLevel(int level) { this.level = level; }
}