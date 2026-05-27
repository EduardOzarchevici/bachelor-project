package org.fitblocker.controller;

import org.fitblocker.model.UserStats;
import org.fitblocker.security.UserPrincipal;
import org.fitblocker.service.StatsService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/stats")
public class StatsController {

    private final StatsService statsService;

    public StatsController(StatsService statsService) {
        this.statsService = statsService;
    }

    @GetMapping
    public ResponseEntity<UserStats> getStats(@AuthenticationPrincipal UserPrincipal principal) {
        return ResponseEntity.ok(statsService.getUserStats(principal.getId()));
    }
}