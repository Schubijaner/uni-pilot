import type Module from 'module';
import baseUrl from './baseUrl';



interface GetModulesByStudyProgramResponse {
    items: Module[];
    total: number;
    limit: number;
    offset: number;
}

interface GetModulesByStudyProgramParams {
    module_type?: 'REQUIRED' | 'ELECTIVE';
    semester?: number;
    limit?: number;
    offset?: number;
}

export async function getModulesByStudyProgram(
    studyProgramId: number,
    params?: GetModulesByStudyProgramParams
): Promise<GetModulesByStudyProgramResponse> {
    const queryParams = new URLSearchParams();

    if (params?.module_type) {
        queryParams.append('module_type', params.module_type);
    }
    if (params?.semester !== undefined) {
        queryParams.append('semester', params.semester.toString());
    }
    if (params?.limit !== undefined) {
        queryParams.append('limit', params.limit.toString());
    }
    if (params?.offset !== undefined) {
        queryParams.append('offset', params.offset.toString());
    }

    const url = `${baseUrl}/study-programs/${studyProgramId}/modules${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Failed to fetch modules: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
}