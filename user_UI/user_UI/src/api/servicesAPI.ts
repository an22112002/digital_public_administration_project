import HUB_api from "./base"

export interface Service {
    serviceID: string
    title: string
    realTitle: string
    category: string
}

export async function getServicesList() {
    const response = await HUB_api.get("/services/active");
    return response.data as Service[];
}

export async function getCategories() {
    const response = await HUB_api.get("/services/categories");
    return response.data as string[];
}