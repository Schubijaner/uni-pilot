import baseUrl from './baseUrl';

interface Skill {
  label: string;
  value: number;
}

interface CreateUserParams {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  universityId: number;
  studyProgramId: number;
  completedModules: number[];
  skills: Skill[];
}

interface RegisterResponse {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  created_at: string;
  token: string; // Assuming token is returned on registration
}

interface ProfileResponse {
  id: number;
  user_id: number;
  university_id: number;
  study_program_id: number;
  current_semester: number;
  skills: string;
  selected_topic_field_id: number | null;
  created_at: string;
  updated_at: string;
}

interface CreateUserResponse {
  token: string;
}

export async function createUser(params: CreateUserParams): Promise<CreateUserResponse> {
  const {
    email,
    password,
    firstName,
    lastName,
    universityId,
    studyProgramId,
    completedModules,
    skills,
  } = params;

  // Step 1: Register the user
  const registerResponse = await fetch(`${baseUrl}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    }),
  });

  if (!registerResponse.ok) {
    const errorData = await registerResponse.json().catch(() => ({}));
    if (registerResponse.status === 400) {
      throw new Error(errorData.message || 'E-Mail bereits vorhanden oder ungültige Daten');
    }
    if (registerResponse.status === 422) {
      throw new Error(errorData.message || 'Validierungsfehler');
    }
    throw new Error(`Registration failed: ${registerResponse.statusText}`);
  }

  //Step 1.5: Get token
  const logInResponse = await fetch(`${baseUrl}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  if (!logInResponse.ok) {
    const errorData = await logInResponse.json().catch(() => ({}));
    if (logInResponse.status === 400) {
      throw new Error(errorData.message || 'Ungültige Anmeldedaten');
    }
    if (logInResponse.status === 422) {
      throw new Error(errorData.message || 'Validierungsfehler');
    }
    throw new Error(`Login failed: ${logInResponse.statusText}`);
  }

  const loginData = await logInResponse.json();
  const token = loginData.access_token;
  const userData = loginData.user as RegisterResponse;

  // Step 2: Create/Update user profile
  const skillsString = skills.map((s) => `${s.label}:${s.value}`).join(', ');

  const profileResponse = await fetch(`${baseUrl}/users/me/profile`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      university_id: universityId,
      study_program_id: studyProgramId,
      current_semester: 1, // Default to 1, can be made configurable
      skills: skillsString,
    }),
  });

  if (!profileResponse.ok) {
    throw new Error(`Failed to create profile: ${profileResponse.statusText}`);
  }

  const profileData: ProfileResponse = await profileResponse.json();

  // Step 3: Update completed modules
  const modulePromises = completedModules.map((moduleId) =>
    fetch(`${baseUrl}/users/me/modules/${moduleId}/progress`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        completed: true,
        completed_at: new Date().toISOString(),
      }),
    })
  );

  await Promise.all(modulePromises);

  return {
    token: token,
  };
}

export default createUser;