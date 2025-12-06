import baseUrl from './baseUrl';
import type { Skill } from '~/types';

interface GetSkillsFromTextResponse {
    skills: Skill[];
    confidence: number;
}

export async function getSkillsFromText(text: string): Promise<GetSkillsFromTextResponse> {
    // Mock response for now
    return {
        skills: [
            { name: 'Python', value: 85 },
            { name: 'React', value: 70 },
            { name: 'TypeScript', value: 65 },
            { name: 'SQL', value: 75 },
            { name: 'Git', value: 80 },
            { name: 'Machine Learning', value: 60 },
        ],
        confidence: 0.85,
    };

    // Actual API call (uncomment when backend is ready)
    // const response = await fetch(`${baseUrl}/skills/extract`, {
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify({ text }),
    // });
    //
    // if (!response.ok) {
    //     throw new Error(`Failed to extract skills: ${response.statusText}`);
    // }
    //
    // return response.json();
}