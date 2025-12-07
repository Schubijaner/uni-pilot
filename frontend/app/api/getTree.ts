import baseUrl from './baseUrl';

interface TopicField {
    id: number;
    name: string;
    description: string;
}

interface CareerTreeNode {
    id: number;
    name: string;
    description: string;
    is_leaf: boolean;
    level: number;
    topic_field?: TopicField;
    children: CareerTreeNode[];
}

interface CareerTreeResponse {
    study_program_id: number;
    nodes: CareerTreeNode | CareerTreeNode[] | null; // Backend kann einzelnes Node oder Array zurückgeben
}

export async function getTree(
    studyProgramId: number,
    token?: string
): Promise<CareerTreeResponse> {
    const url = `${baseUrl}/study-programs/${studyProgramId}/career-tree`;
    
    const headers: HeadersInit = {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, { headers });
    
    if (!response.ok) {
        throw new Error(`Failed to fetch career tree: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Backend gibt nodes als einzelnes Objekt zurück (CareerTreeNodeResponse), nicht als Array
    // Wir müssen es in ein Array umwandeln, damit das Frontend konsistent damit arbeiten kann
    if (data && data.nodes) {
        // Wenn nodes ein einzelnes Objekt ist, mache es zu einem Array
        if (!Array.isArray(data.nodes)) {
            data.nodes = [data.nodes];
        }
    } else {
        // Wenn nodes null oder undefined ist, setze es auf leeres Array
        data.nodes = [];
    }
    
    return data as CareerTreeResponse & { nodes: CareerTreeNode[] };
}