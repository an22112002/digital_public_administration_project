import HUB_api from "./base";
import type { UpdateResponse } from "./base";

export interface NAPS2PathResponse {
    naps2_path: string;
}

export interface TitleResponse {
    title: string;
}

interface ProvinceOption {
    name: string;
    id: string;
}

export interface CommuneListResponse {
    commune_list: CommuneOption[];
}

interface CommuneOption {
    name: string;
    id: string;
}

export interface ProvinceListResponse {
    province_list: ProvinceOption[];
}

export async function getNAPS2Path() {
    const response = await HUB_api.get("/settings/naps2-path");
    return response.data as NAPS2PathResponse;
}

export async function saveNAPS2Path(path: string) {
    const response = await HUB_api.put("/settings/naps2-path", { path: path });
    return response.data as UpdateResponse;
}

export async function getTitle() {
    const response = await HUB_api.get("/settings/title");
    return response.data as TitleResponse;
}

export async function saveTitle(title: string) {
    const response = await HUB_api.put("/settings/title", { title: title });
    return response.data as UpdateResponse;
}

export async function getProvince() {
    const response = await HUB_api.get("/settings/province");
    return response.data as { province: string };
}

export async function getCommune() {
    const response = await HUB_api.get("/settings/commune");
    return response.data as { commune: string };
}

export async function listProvince() {
    const response = await HUB_api.get("/settings/province-list");
    return response.data as ProvinceListResponse;
}

export async function listCommune(id: string) {
    const response = await HUB_api.get(`/settings/commune-list/${id}`);
    return response.data as CommuneListResponse;
}

export async function saveNewPosition(provinceID: string, communeID: string) {
    const response = await HUB_api.put(`/settings/position`, { provinceID: provinceID, communeID: communeID });
    return response.data as UpdateResponse;
}