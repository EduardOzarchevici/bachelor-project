package org.fitblocker.model;


import jakarta.persistence.*;
import com.fasterxml.jackson.annotation.JsonIgnore;

@Entity
@Table(name = "user_stats")
public class UserStats {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private int xp = 0;
    private int pushupsTarget = 5;

    @JsonIgnore
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private AppUser user;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public int getXp() { return xp; }
    public void setXp(int xp) { this.xp = xp; }
    public int getPushupsTarget() { return pushupsTarget; }
    public void setPushupsTarget(int pushupsTarget) { this.pushupsTarget = pushupsTarget; }
    public AppUser getUser() { return user; }
    public void setUser(AppUser user) { this.user = user; }
}