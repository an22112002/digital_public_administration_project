import HUB_api from "./base"

export interface Service {
    serviceID: string
    title: string
    realTitle: string
    category: string
}

export async function getServicesList(category?: string, title?: string) {
    const response = await HUB_api.get<Service[]>('/services/service-list', {
        params: {
            category: category || undefined,
            title: title || undefined,
        },
    });
    return response.data;
}

export async function getCategories() {
    const response = await HUB_api.get<string[]>('/services/categories');
    return response.data;
}
