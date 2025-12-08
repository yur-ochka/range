import api from "./axiosInstance";
import type { Category } from "@/types/catalog";

export async function getCategories(): Promise<{ results: Category[] }> {
    const res = await api.get("/catalog/categories/");
    return res.data;
}
