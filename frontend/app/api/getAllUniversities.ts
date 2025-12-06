import baseUrl from './baseUrl';

interface University {
    id: number;
    name: string;
    abbreviation: string;
    created_at: string;
}

interface GetAllUniversitiesResponse {
    items: University[];
    total: number;
    limit: number;
    offset: number;
}

interface GetAllUniversitiesParams {
    search?: string;
    limit?: number;
    offset?: number;
}

export async function getAllUniversities(
    params?: GetAllUniversitiesParams
): Promise<GetAllUniversitiesResponse> {
    return {
            "items": [
                {
                "id": 1,
                "name": "Technische Universität München",
                "abbreviation": "TUM",
                "created_at": "2024-01-01T00:00:00Z"
                }
            ],
            "total": 1,
            "limit": 100,
            "offset": 0
            };
    const queryParams = new URLSearchParams();
    
    if (params?.search) {
        queryParams.append('search', params.search);
    }
    if (params?.limit !== undefined) {
        queryParams.append('limit', params.limit.toString());
    }
    if (params?.offset !== undefined) {
        queryParams.append('offset', params.offset.toString());
    }

    const url = `${baseUrl}/universities${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
        throw new Error(`Failed to fetch universities: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
}