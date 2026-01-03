import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

// =========================================================
// Response Interfaces
// =========================================================

export interface InitResponse {
    success: boolean;
    message: string;
}

export interface ChatResponse {
    success: boolean;
    message: string;
    trace: TraceStep[];
}

export interface TraceStep {
    step_id: number;
    action: any;
    success: boolean;
    result: string | null;
    observation: string | null;
    error: string | null;
    timestamp: number;
}

export interface StatusResponse {
    initialized: boolean;
    gpu: string;
    llm_provider: string | null;
}

export interface SetProviderResponse {
    success: boolean;
    message: string;
    provider: string | null;
}

export interface ProviderStatus {
    healthy: boolean;
    model: string;
    current: boolean;
    error?: string;
}

export interface LLMStatusResponse {
    current_provider: string | null;
    providers: { [key: string]: ProviderStatus };
    available: string[];
}

// =========================================================
// API Service
// =========================================================

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private baseUrl = 'http://localhost:8000/api';

    // Reactive signals for state
    isInitialized = signal(false);
    gpuStatus = signal('Not active');
    currentProvider = signal<string>('ollama');
    availableProviders = signal<string[]>(['ollama', 'gemini']);

    constructor(private http: HttpClient) {
        this.checkStatus();
    }

    // =========================================================
    // Status & Initialization
    // =========================================================

    async checkStatus(): Promise<StatusResponse> {
        try {
            const response = await firstValueFrom(
                this.http.get<StatusResponse>(`${this.baseUrl}/status`)
            );
            this.isInitialized.set(response.initialized);
            this.gpuStatus.set(response.gpu);
            if (response.llm_provider) {
                this.currentProvider.set(response.llm_provider);
            }
            return response;
        } catch (error) {
            console.error('Failed to check status:', error);
            return { initialized: false, gpu: 'Error', llm_provider: null };
        }
    }

    async initialize(provider: string = 'ollama'): Promise<InitResponse> {
        try {
            const response = await firstValueFrom(
                this.http.post<InitResponse>(`${this.baseUrl}/initialize`, { provider })
            );
            if (response.success) {
                this.isInitialized.set(true);
                this.currentProvider.set(provider);
            }
            return response;
        } catch (error: any) {
            return {
                success: false,
                message: error?.message || 'Failed to initialize'
            };
        }
    }

    // =========================================================
    // Chat
    // =========================================================

    async sendMessage(message: string): Promise<ChatResponse> {
        try {
            return await firstValueFrom(
                this.http.post<ChatResponse>(`${this.baseUrl}/chat`, { message })
            );
        } catch (error: any) {
            return {
                success: false,
                message: error?.error?.detail || error?.message || 'Request failed',
                trace: []
            };
        }
    }

    // =========================================================
    // LLM Provider Management
    // =========================================================

    async setLLMProvider(provider: string): Promise<SetProviderResponse> {
        try {
            const response = await firstValueFrom(
                this.http.post<SetProviderResponse>(`${this.baseUrl}/llm/provider`, { provider })
            );
            if (response.success && response.provider) {
                this.currentProvider.set(response.provider);
            }
            return response;
        } catch (error: any) {
            return {
                success: false,
                message: error?.error?.detail || error?.message || 'Failed to switch provider',
                provider: null
            };
        }
    }

    async getLLMStatus(): Promise<LLMStatusResponse> {
        try {
            const response = await firstValueFrom(
                this.http.get<LLMStatusResponse>(`${this.baseUrl}/llm/status`)
            );
            if (response.current_provider) {
                this.currentProvider.set(response.current_provider);
            }
            if (response.available) {
                this.availableProviders.set(response.available);
            }
            return response;
        } catch (error) {
            console.error('Failed to get LLM status:', error);
            return {
                current_provider: null,
                providers: {},
                available: []
            };
        }
    }
}
