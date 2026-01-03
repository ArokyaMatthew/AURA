import { Component, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, LLMStatusResponse } from '../../services/api.service';

@Component({
    selector: 'app-settings',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './settings.component.html',
    styleUrl: './settings.component.scss'
})
export class SettingsComponent implements OnInit {
    isOpen = signal(false);
    isLoading = signal(false);
    statusMessage = signal<string | null>(null);

    // Provider status from API
    providerHealth = signal<{ [key: string]: boolean }>({});

    constructor(public api: ApiService) { }

    ngOnInit() {
        this.refreshStatus();
    }

    toggle() {
        this.isOpen.update(v => !v);
        if (this.isOpen()) {
            this.refreshStatus();
        }
    }

    close() {
        this.isOpen.set(false);
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
