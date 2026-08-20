import axios from "axios";

const backendUrl = "http://localhost:8000";

const HUB_api = axios.create({
    baseURL: backendUrl,
});

export default HUB_api;

export interface UpdateResponse {
    success: boolean;
    message: string;
    error: string | null;
}