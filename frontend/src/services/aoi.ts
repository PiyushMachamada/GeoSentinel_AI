import type { AOI } from "@/types/aoi";

const API_URL = "http://127.0.0.1:8000";

export async function getAOIs(): Promise<AOI[]> {

    const response = await fetch(
        `${API_URL}/aois/`
    );

    if (!response.ok) {
        throw new Error("Failed to fetch AOIs");
    }

    return response.json();
}