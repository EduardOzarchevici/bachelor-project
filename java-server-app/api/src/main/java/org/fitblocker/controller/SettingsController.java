package org.fitblocker.controller;

import org.fitblocker.dto.PushupsSettingsRequest;
import org.fitblocker.dto.PushupsSettingsResponse;
import org.fitblocker.service.SettingsService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/settings")
public class SettingsController {

    private final SettingsService settingsService;

    public SettingsController(SettingsService settingsService) {
        this.settingsService = settingsService;
    }

    @GetMapping("/pushups")
    public ResponseEntity<PushupsSettingsResponse> getPushupsTarget(Authentication authentication) {
        return ResponseEntity.ok(settingsService.getPushupsTarget(authentication.getName()));
    }

    @PutMapping("/pushups")
    public ResponseEntity<PushupsSettingsResponse> updatePushupsTarget(
            @RequestBody PushupsSettingsRequest request,
            Authentication authentication) {
        return ResponseEntity.ok(settingsService.updatePushupsTarget(authentication.getName(), request));
    }
}