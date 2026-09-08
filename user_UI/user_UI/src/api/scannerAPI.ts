import HUB_api from "./base"

export interface ScannerDevice {
    name: string;
    status: "connected" | "disconnected";
    driver: string[];
}

export interface ScannerOption {
    id: string;
    label: string;
    scanner: string;
    driver: string;
    status: "connected" | "disconnected";
}

export interface DevicesListResponse {
    wia: ScannerDevice[];
    twain: ScannerDevice[];
    escl: ScannerDevice[];
}

export interface ScannerOptionsResponse {
    options: ScannerOption[];
    default?: ScannerOption | null;
}

export async function getDevicesList() {
    const response = await HUB_api.get("/scanner/naps2/devices");
    return response.data as DevicesListResponse;
}

export async function getScannerOptions() {
    const response = await HUB_api.get("/scanner/naps2/options");
    return response.data as ScannerOptionsResponse;
}