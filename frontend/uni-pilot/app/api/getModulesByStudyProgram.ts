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
    return {
  "items": [
    {
      "id": 1,
      "name": "Analysis I und Lineare Algebra für Ingenieurwissenschaften",
      "description": "Grundlagen der Analysis und Linearen Algebra",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 1,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 2,
      "name": "Programmieren I",
      "description": "Einführung in die Grundlagen der Programmierung",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 1,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 3,
      "name": "Einführung in die Wirtschaftsinformatik",
      "description": "Grundlagen und Anwendungsfelder der Wirtschaftsinformatik",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 1,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 4,
      "name": "Theoretische Grundlagen der Informatik",
      "description": "Formale Sprachen, Automaten und Berechenbarkeit",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 1,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 5,
      "name": "Statistik I für Wirtschaftswissenschaften",
      "description": "Deskriptive Statistik und Wahrscheinlichkeitsrechnung",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 2,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 6,
      "name": "Architektur von Anwendungssystemen",
      "description": "Aufbau und Entwurf von Anwendungssystemen",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 2,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 7,
      "name": "Programmieren II",
      "description": "Fortgeschrittene Programmierkonzepte und -techniken",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 2,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 8,
      "name": "Bilanzierung und Kostenrechnung",
      "description": "Grundlagen des externen und internen Rechnungswesens",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 2,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 9,
      "name": "Organisation und Innovationsmanagement",
      "description": "Grundlagen der Betrieblichen Organisation und des Innovationsmanagements",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 2,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 10,
      "name": "Statistik II für Wirtschaftswissenschaften",
      "description": "Induktive Statistik und Schätzverfahren",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 3,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 11,
      "name": "Technische Grundlagen der Informatik",
      "description": "Digitaltechnik und Rechnerarchitektur",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 3,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 12,
      "name": "Softwaretechnik und Programmierparadigmen",
      "description": "Softwareentwicklungsprozesse und verschiedene Programmierstile",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 3,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 13,
      "name": "Operations Research - Grundlagen",
      "description": "Einführung in die mathematische Optimierung",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 3,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 14,
      "name": "Marketing und Produktionsmanagement",
      "description": "Grundlagen des Marketings und der Produktionsplanung",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 3,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 15,
      "name": "Informationssysteme und Datenanalyse",
      "description": "Datenbanken, Data Warehousing und Analysemethoden",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 4,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 16,
      "name": "Einführung in die IT-Sicherheit",
      "description": "Grundlagen und Konzepte der IT-Sicherheit",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 4,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 17,
      "name": "Wahlpflicht-Programmierpraktikum",
      "description": "Praktische Anwendung von Programmierkenntnissen (Wahlpflicht)",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 4,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 18,
      "name": "Geschäftsprozesse",
      "description": "Modellierung, Analyse und Optimierung von Geschäftsprozessen",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 4,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 19,
      "name": "Investition und Finanzierung",
      "description": "Grundlagen der Investitionsrechnung und Unternehmensfinanzierung",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 4,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 20,
      "name": "Wahlpflichtbereich",
      "description": "Ausgewählte Vertiefungsmodule (30-33 LP)",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 5,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 21,
      "name": "Wahlbereich",
      "description": "Module zur freien Wahl (12-15 LP)",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 5,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 22,
      "name": "Informatik und Gesellschaft",
      "description": "Ethische und gesellschaftliche Aspekte der Informatik",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 5,
      "created_at": "2025-12-06T00:00:00Z"
    },
    {
      "id": 23,
      "name": "Bachelorarbeit",
      "description": "Wissenschaftliche Abschlussarbeit (12 LP)",
      "module_type": "REQUIRED",
      "study_program_id": 1,
      "semester": 6,
      "created_at": "2025-12-06T00:00:00Z"
    }
  ],
  "total": 23,
  "limit": 100,
  "offset": 0
};

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