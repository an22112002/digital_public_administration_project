import axios from "axios";

const HUB_api = axios.create({
    baseURL: "http://localhost:8000",
});

export default HUB_api;

export interface UpdateResponse {
    success: boolean;
    message: string;
    error: string | null;
}