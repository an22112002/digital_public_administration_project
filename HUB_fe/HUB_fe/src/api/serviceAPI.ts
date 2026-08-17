import HUB_api from "./base";
import type { UpdateResponse } from "./base";

export async function importFileXLSX(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await HUB_api.post("/services/xlsx", formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });
    return response.data as UpdateResponse;
}