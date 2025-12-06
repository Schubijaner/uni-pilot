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
    nodes: CareerTreeNode[];
}

export async function getTree(
    token: string,
    studyProgramId: number
): Promise<CareerTreeResponse> {
    return {
        study_program_id: 1,
        nodes: [
            {
                id: 1,
                name: "Software Development",
                description: "Entwicklung von Software-Anwendungen",
                is_leaf: false,
                level: 1,
                questions: [
                    { id: 1, question_text: "Interessierst du dich für Frontend-Entwicklung?", answer: true },
                    { id: 2, question_text: "Arbeitest du gerne mit Datenbanken?", answer: false },
                    { id: 3, question_text: "Interessierst du dich für Machine Learning?", answer: true },
                    { id: 4, question_text: "Möchtest du im Bereich Cybersecurity arbeiten?", answer: false },
                    { id: 5, question_text: "Bist du an mobiler App-Entwicklung interessiert?", answer: true },
                    { id: 6, question_text: "Arbeitest du gerne im Team?", answer: true },
                    { id: 7, question_text: "Interessierst du dich für Cloud Computing?", answer: true },
                    { id: 8, question_text: "Möchtest du in der Spieleentwicklung arbeiten?", answer: false }
                ],
                children: [
                    {
                        id: 2,
                        name: "Full Stack Development",
                        description: "Frontend und Backend Entwicklung",
                        is_leaf: true,
                        level: 2,
                        topic_field: {
                            id: 1,
                            name: "Full Stack Development",
                            description: "Komplette Web-Entwicklung"
                        },
                        questions: [
                            { id: 9, question_text: "Hast du Erfahrung mit React oder Vue?", answer: true },
                            { id: 10, question_text: "Kennst du dich mit REST APIs aus?", answer: true }
                        ],
                        children: []
                    },
                    {
                        id: 3,
                        name: "Data Science",
                        description: "Analyse von großen Datenmengen",
                        is_leaf: false,
                        level: 2,
                        questions: [
                            { id: 11, question_text: "Arbeitest du gerne mit Statistik?", answer: true },
                            { id: 12, question_text: "Interessierst du dich für Datenvisualisierung?", answer: true }
                        ],
                        children: [
                            {
                                id: 4,
                                name: "Machine Learning",
                                description: "AI und neuronale Netze",
                                is_leaf: true,
                                level: 3,
                                topic_field: {
                                    id: 2,
                                    name: "Machine Learning",
                                    description: "Künstliche Intelligenz und Deep Learning"
                                },
                                questions: [
                                    { id: 13, question_text: "Hast du Erfahrung mit Python?", answer: true },
                                    { id: 14, question_text: "Kennst du TensorFlow oder PyTorch?", answer: false }
                                ],
                                children: []
                            },
                            {
                                id: 5,
                                name: "Data Engineering",
                                description: "Dateninfrastruktur und Pipelines",
                                is_leaf: true,
                                level: 3,
                                topic_field: {
                                    id: 3,
                                    name: "Data Engineering",
                                    description: "ETL-Prozesse und Datenarchitektur"
                                },
                                questions: [
                                    { id: 15, question_text: "Hast du Erfahrung mit SQL?", answer: true },
                                    { id: 16, question_text: "Kennst du Apache Spark?", answer: false }
                                ],
                                children: []
                            }
                        ]
                    },
                    {
                        id: 6,
                        name: "Mobile Development",
                        description: "Entwicklung mobiler Anwendungen",
                        is_leaf: false,
                        level: 2,
                        questions: [
                            { id: 17, question_text: "Besitzt du ein Smartphone?", answer: true },
                            { id: 18, question_text: "Interessierst du dich für UI/UX Design?", answer: true }
                        ],
                        children: [
                            {
                                id: 7,
                                name: "iOS Development",
                                description: "Native iOS App-Entwicklung",
                                is_leaf: true,
                                level: 3,
                                topic_field: {
                                    id: 4,
                                    name: "iOS Development",
                                    description: "Swift und SwiftUI Entwicklung"
                                },
                                questions: [
                                    { id: 19, question_text: "Hast du einen Mac?", answer: true },
                                    { id: 20, question_text: "Kennst du Swift?", answer: false }
                                ],
                                children: []
                            },
                            {
                                id: 8,
                                name: "Android Development",
                                description: "Native Android App-Entwicklung",
                                is_leaf: true,
                                level: 3,
                                topic_field: {
                                    id: 5,
                                    name: "Android Development",
                                    description: "Kotlin und Jetpack Compose"
                                },
                                questions: [
                                    { id: 21, question_text: "Hast du Erfahrung mit Java?", answer: true },
                                    { id: 22, question_text: "Kennst du Kotlin?", answer: false }
                                ],
                                children: []
                            }
                        ]
                    }
                ]
            },
            {
                id: 9,
                name: "IT Infrastructure",
                description: "Verwaltung und Betrieb von IT-Systemen",
                is_leaf: false,
                level: 1,
                questions: [
                    { id: 23, question_text: "Interessierst du dich für Netzwerke?", answer: true },
                    { id: 24, question_text: "Arbeitest du gerne mit Linux?", answer: true }
                ],
                children: [
                    {
                        id: 10,
                        name: "Cloud Computing",
                        description: "Cloud-Dienste und -Architektur",
                        is_leaf: true,
                        level: 2,
                        topic_field: {
                            id: 6,
                            name: "Cloud Computing",
                            description: "AWS, Azure und GCP"
                        },
                        questions: [
                            { id: 25, question_text: "Hast du Erfahrung mit AWS?", answer: true },
                            { id: 26, question_text: "Kennst du Docker und Kubernetes?", answer: true }
                        ],
                        children: []
                    },
                    {
                        id: 11,
                        name: "Cybersecurity",
                        description: "IT-Sicherheit und Datenschutz",
                        is_leaf: true,
                        level: 2,
                        topic_field: {
                            id: 7,
                            name: "Cybersecurity",
                            description: "Netzwerksicherheit und Penetration Testing"
                        },
                        questions: [
                            { id: 27, question_text: "Interessierst du dich für Ethical Hacking?", answer: true },
                            { id: 28, question_text: "Kennst du OWASP?", answer: false }
                        ],
                        children: []
                    }
                ]
            }
        ]
    };

    const url = `${baseUrl}/study-programs/${studyProgramId}/career-tree`;
    
    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (!response.ok) {
        throw new Error(`Failed to fetch career tree: ${response.statusText}`);
    }
    
    return response.json();
}