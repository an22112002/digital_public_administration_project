import HUB_api from "./base";

export interface Naps2InstalledResponse {
    installed: boolean;
    message: string;
}

export interface ScannerDevice {
    name: string;
    status: "connected" | "disconnected";
    driver: string[];
}

export interface DevicesListResponse {
    wia: ScannerDevice[];
    twain: ScannerDevice[];
    escl: ScannerDevice[];
}

export async function getNaps2Installed() {
    const response = await HUB_api.get("/scanner/naps2/installed");
    return response.data as Naps2InstalledResponse;
}

export async function getDevicesList() {
    const response = await HUB_api.get("/scanner/naps2/devices");
    return response.data as DevicesListResponse;
}