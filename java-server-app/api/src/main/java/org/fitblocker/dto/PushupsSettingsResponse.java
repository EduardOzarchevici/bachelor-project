package org.fitblocker.dto;

public class PushupsSettingsResponse {
    private int pushupsTarget;

    public PushupsSettingsResponse() {
    }

    public PushupsSettingsResponse(int pushupsTarget) {
        this.pushupsTarget = pushupsTarget;
    }

    public int getPushupsTarget() {
        return pushupsTarget;
    }

    public void setPushupsTarget(int pushupsTarget) {
        this.pushupsTarget = pushupsTarget;
    }
}

