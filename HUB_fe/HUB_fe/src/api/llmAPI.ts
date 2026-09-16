import HUB_api from "./base";
import type { UpdateResponse } from "./base";

export interface LLMSetting {
    LLM_model: string;
    LLM_gpu_use: number;
    LLM_context_length: number;
}

export interface LLMServerStatus {
    state: boolean;
}

export async function getLLMModels() {
    const response = await HUB_api.get<string[]>("/settings/llm-models");
    return response.data;
}

export async function getLLMSetting() {
    const response = await HUB_api.get<LLMSetting>("/settings/llm");
    const setting = response.data;
    const gpuUse = Number(setting.LLM_gpu_use);
    const contextLength = Number(setting.LLM_context_length);

    return {
        ...setting,
        LLM_gpu_use: Number.isFinite(gpuUse) ? gpuUse : 0,
        LLM_context_length: Number.isFinite(contextLength) ? contextLength : 8192,
    };
}

export async function updateLLMSetting(setting: LLMSetting) {
    const response = await HUB_api.put<UpdateResponse>("/settings/llm-update", {
        model: setting.LLM_model,
        gpu_use: setting.LLM_gpu_use,
        context_length: setting.LLM_context_length,
    });
    return response.data;
}

export async function getLLMServerStatus() {
    const response = await HUB_api.get<LLMServerStatus>("/settings/llm-server-status");
    return response.data;
}

export async function loadLLMModel() {
    const response = await HUB_api.post<UpdateResponse>("/settings/llm-load");
    return response.data;
}

export async function unloadLLMModel() {
    const response = await HUB_api.post<UpdateResponse>("/settings/llm-unload");
    return response.data;
}
