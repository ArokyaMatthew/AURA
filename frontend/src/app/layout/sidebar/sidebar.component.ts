import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../services/api.service';
import { SettingsService } from '../../services/settings.service';

interface NavItem {
  icon: string;
  label: string;
  active?: boolean;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule, MatTooltipModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent {
  private apiService = inject(ApiService);
  private settingsService = inject(SettingsService);

  navItems: NavItem[] = [
    { icon: 'chat', label: 'Chat', active: true },
    { icon: 'settings', label: 'Settings' }
  ];

  isInitialized = this.apiService.isInitialized;
  isLoading = signal(false);
  initError = signal<string | null>(null);

  onNavClick(item: NavItem) {
    if (item.label === 'Settings') {
      this.settingsService.open();
    }
    // Chat is already the default view, no action needed
  }

  async initializeAgent() {
    this.isLoading.set(true);
    this.initError.set(null);

    const result = await this.apiService.initialize();

    if (!result.success) {
      this.initError.set(result.message);
    }

    this.isLoading.set(false);
  }

  dismissError() {
    this.initError.set(null);
  }
}
