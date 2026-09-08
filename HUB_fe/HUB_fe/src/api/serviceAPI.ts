import HUB_api from "./base";
import type { UpdateResponse } from "./base";

export interface Service {
    serviceID: string | number;
    title: string;
    realTitle: string;
    category: string;
    active: boolean;
}

export async function getServices() {
    const response = await HUB_api.get<Service[]>('/services/all');
    return response.data;
}

export async function updateServiceActive(serviceId: Service['serviceID'], active: boolean) {
    const response = await HUB_api.put<UpdateResponse>(`/services/${serviceId}/active`, { active });
    return response.data;
}