import HUB_api from "./base"

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

export async function getDevicesList() {
    const response = await HUB_api.get("/scanner/naps2/devices");
    return response.data as DevicesListResponse;
}