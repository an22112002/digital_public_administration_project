import HUB_api from "./base";

export interface TwainInstalledResponse {
    installed: boolean;
    message: string;
}

export interface ScannerDevice {
    name: string;
    status: "connected" | "disconnected";
}

export interface ScannerOption {
    id: string;
    label: string;
    scanner: string;
    driver: "twain";
    status: ScannerDevice["status"];
}

export interface ScannerOptionsResponse {
    options: ScannerOption[];
    default: ScannerOption | null;
}

export async function getTwainInstalled() {
    const response = await HUB_api.get("/scanner/twain/installed");
    return response.data as TwainInstalledResponse;
}

export async function getTwainDevices() {
    const response = await HUB_api.get<{ twain: ScannerDevice[] }>("/scanner/twain/devices");
    return response.data;
}

export async function getTwainOptions() {
    const response = await HUB_api.get<ScannerOptionsResponse>("/scanner/twain/options");
    return response.data;
}