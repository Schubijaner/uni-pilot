import baseUrl from './baseUrl';

interface StudyProgram {
    id: number;
    name: string;
    university_id: number;
    degree_type: string;
    created_at: string;
}

interface GetStudyProgramsByUniversityResponse {
    items: StudyProgram[];
    total: number;
}

interface GetStudyProgramsByUniversityParams {
    degree_type?: string;
}

export async function getStudyProgramsByUniversity(
    universityId: number,
    params?: GetStudyProgramsByUniversityParams
): Promise<GetStudyProgramsByUniversityResponse> {
    const queryParams = new URLSearchParams();
    
    if (params?.degree_type) {
        queryParams.append('degree_type', params.degree_type);
    }

    const url = `${baseUrl}/universities/${universityId}/study-programs${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
        throw new Error(`Failed to fetch study programs: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
}