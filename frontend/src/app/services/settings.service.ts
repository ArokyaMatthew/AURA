import { Injectable, signal } from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class SettingsService {
    // Shared signal for settings panel state
    isOpen = signal(false);

    toggle() {
        this.isOpen.update(v => !v);
    }

    open() {
        this.isOpen.set(true);
    }

    close() {
        this.isOpen.set(false);
    }
}
