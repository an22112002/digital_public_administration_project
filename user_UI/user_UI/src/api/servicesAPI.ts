import HUB_api from "./base"

export interface Service {
    serviceID: string
    title: string
    realTitle: string
    category: string
}

export async function getServicesList(category?: string, title?: string) {
    let url_extension = '';
    if (category === undefined || category === null || category === '') {
        
    } else {
        url_extension += `?category=${category}`;
    }
    if (title === undefined || title === null || title === '') {
    } else {
        if (url_extension !== '') {
            url_extension += '&';
        } else {
            url_extension += '?';
        }
        url_extension += `title=${title}`;
    }
    const response = await HUB_api.get(`/services/service-list${url_extension}`);
    return response.data as Service[];
}

export async function getCategories() {
    const response = await HUB_api.get("/services/categories");
    return response.data as string[];
}