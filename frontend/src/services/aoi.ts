import type { AOI } from "@/types/aoi";

const API_URL = "http://127.0.0.1:8000";

export async function getAOIs(): Promise<AOI[]> {
    const response = await fetch(
        `${API_URL}/aois/`,
        { cache: "no-store" }
    );

    if (!response.ok) {
        throw new Error("Failed to fetch AOIs");
    }

    const data: AOI[] | { aois: AOI[] } =
        await response.json();

    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data.aois)) {
        return data.aois;
    }

    throw new Error("Unexpected AOI response.");
}