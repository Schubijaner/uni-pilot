import type { UserQuestion } from '~/types';
import baseUrl from './baseUrl';

interface GetUserQuestionsResponse {
    items: UserQuestion[];
    total: number;
    limit: number;
    offset: number;
}

interface GetUserQuestionsParams {
    career_tree_node_id?: number;
    limit?: number;
    offset?: number;
}

export async function getUserQuestions(
    token: string,
    params?: GetUserQuestionsParams
): Promise<GetUserQuestionsResponse> {
    const queryParams = new URLSearchParams();
    
    if (params?.career_tree_node_id !== undefined) {
        queryParams.append('career_tree_node_id', params.career_tree_node_id.toString());
    }
    if (params?.limit !== undefined) {
        queryParams.append('limit', params.limit.toString());
    }
    if (params?.offset !== undefined) {
        queryParams.append('offset', params.offset.toString());
    }

    const url = `${baseUrl}/users/me/questions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    
    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (!response.ok) {
        throw new Error(`Failed to fetch user questions: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
}