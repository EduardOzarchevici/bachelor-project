package org.fitblocker.controller;

import org.fitblocker.dto.PushupsSettingsRequest;
import org.fitblocker.dto.PushupsSettingsResponse;
import org.fitblocker.security.UserPrincipal;
import org.fitblocker.service.SettingsService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/settings")
public class SettingsController {

    private final SettingsService settingsService;

    public SettingsController(SettingsService settingsService) {
        this.settingsService = settingsService;
    }

    @GetMapping("/pushups")
    public ResponseEntity<PushupsSettingsResponse> getPushupsTarget(@AuthenticationPrincipal UserPrincipal principal) {
        return ResponseEntity.ok(settingsService.getPushupsTarget(principal.getId()));
    }

    @PutMapping("/pushups")
    public ResponseEntity<PushupsSettingsResponse> updatePushupsTarget(
            @RequestBody PushupsSettingsRequest request,
            @AuthenticationPrincipal UserPrincipal principal) {
        return ResponseEntity.ok(settingsService.updatePushupsTarget(principal.getId(), request));
    }
}