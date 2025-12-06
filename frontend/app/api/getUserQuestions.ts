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
    return {
        "items": [
            {
                "id": 1,
                "question_text": "Interessierst du dich für Frontend-Entwicklung?",
                "answer": true,
                "career_tree_node_id": 2,
                "created_at": "2024-01-15T11:30:00Z"
            },
            {
                "id": 2,
                "question_text": "Arbeitest du gerne mit Datenbanken?",
                "answer": false,
                "career_tree_node_id": 3,
                "created_at": "2024-01-15T11:32:00Z"
            },
            {
                "id": 3,
                "question_text": "Interessierst du dich für Machine Learning?",
                "answer": true,
                "career_tree_node_id": 4,
                "created_at": "2024-01-15T11:35:00Z"
            },
            {
                "id": 4,
                "question_text": "Möchtest du im Bereich Cybersecurity arbeiten?",
                "answer": false,
                "career_tree_node_id": 5,
                "created_at": "2024-01-15T11:38:00Z"
            },
            {
                "id": 5,
                "question_text": "Bist du an mobiler App-Entwicklung interessiert?",
                "answer": true,
                "career_tree_node_id": 6,
                "created_at": "2024-01-15T11:40:00Z"
            },
            {
                "id": 6,
                "question_text": "Arbeitest du gerne im Team?",
                "answer": true,
                "career_tree_node_id": 2,
                "created_at": "2024-01-15T11:42:00Z"
            },
            {
                "id": 7,
                "question_text": "Interessierst du dich für Cloud Computing?",
                "answer": true,
                "career_tree_node_id": 7,
                "created_at": "2024-01-15T11:45:00Z"
            },
            {
                "id": 8,
                "question_text": "Möchtest du in der Spieleentwicklung arbeiten?",
                "answer": false,
                "career_tree_node_id": 8,
                "created_at": "2024-01-15T11:48:00Z"
            }
        ],
        "total": 8,
        "limit": 100,
        "offset": 0
    };

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