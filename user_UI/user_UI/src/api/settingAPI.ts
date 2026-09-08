import HUB_api from "./base"

export async function getTitle() {
    const response = await HUB_api.get("/settings/title");
    return response.data as { title: string };
}