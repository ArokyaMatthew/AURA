import { Component, signal, OnInit, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, LLMStatusResponse } from '../../services/api.service';
import { SettingsService } from '../../services/settings.service';

@Component({
    selector: 'app-settings',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './settings.component.html',
    styleUrl: './settings.component.scss'
})
export class SettingsComponent implements OnInit {
    isLoading = signal(false);
    statusMessage = signal<string | null>(null);

    // Provider status from API
    providerHealth = signal<{ [key: string]: boolean }>({});

    constructor(
        public api: ApiService,
        public settings: SettingsService
    ) {
        // Refresh status when panel opens
        effect(() => {
            if (this.settings.isOpen()) {
                this.refreshStatus();
            }
        });
    }

    ngOnInit() {
        this.refreshStatus();
    }

    toggle() {
        this.settings.toggle();
    }

    close() {
        this.settings.close();
    }

    isOpen() {
        return this.settings.isOpen();
    }

    async refreshStatus() {
        const status = await this.api.getLLMStatus();
        const health: { [key: string]: boolean } = {};
        for (const [name, info] of Object.entries(status.providers)) {
            health[name] = info.healthy;
        }
        this.providerHealth.set(health);
    }

    async selectProvider(provider: string) {
        if (provider === this.api.currentProvider()) {
            return; // Already selected
        }

        this.isLoading.set(true);
        this.statusMessage.set(null);

        const result = await this.api.setLLMProvider(provider);

        this.isLoading.set(false);

        if (result.success) {
            this.statusMessage.set(`Switched to ${provider.toUpperCase()}`);
            setTimeout(() => this.statusMessage.set(null), 3000);
        } else {
            this.statusMessage.set(`Error: ${result.message}`);
        }
    }

    async toggleOfflineMode() {
        const currentState = this.api.offlineMode();
        const newState = !currentState;
        this.isLoading.set(true);
        this.statusMessage.set(null);

        try {
            const result = await this.api.setOfflineMode(newState);

            // Check if manual_offline was set correctly (that's what we control)
            // The actual offline_mode might differ if auto-detect kicks in
            if (result.manual_offline === newState) {
                this.statusMessage.set(
                    newState
                        ? '📴 Offline Mode Enabled - AI works without internet!'
                        : '🌐 Online Mode - Full features available'
                );
            } else if (result.offline_mode !== currentState) {
                // Mode changed somehow, show appropriate message
                this.statusMessage.set(
                    result.offline_mode
                        ? '📴 Offline Mode Active'
                        : '🌐 Online Mode Active'
                );
            } else {
                this.statusMessage.set('Mode updated');
            }
        } catch (error) {
            console.error('Toggle offline mode error:', error);
            this.statusMessage.set('Error: Failed to change mode');
        }

        this.isLoading.set(false);
        setTimeout(() => this.statusMessage.set(null), 3000);
    }

    getProviderIcon(provider: string): string {
        const icons: { [key: string]: string } = {
            'ollama': '🦙',
            'gemini': '✨'
        };
        return icons[provider] || '🤖';
    }

    getProviderLabel(provider: string): string {
        const labels: { [key: string]: string } = {
            'ollama': 'Ollama (Local)',
            'gemini': 'Gemini (Cloud)'
        };
        return labels[provider] || provider;
    }
}
