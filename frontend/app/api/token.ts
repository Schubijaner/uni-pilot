import baseUrl from "./baseUrl";

export async function logIn(email: string, password: string): Promise<{ token: string }> {
  const response = await fetch(`${baseUrl}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
    if (!response.ok) {
    throw new Error('Failed to log in');
  }
  const data = await response.json();
  return { token: data.access_token };
}