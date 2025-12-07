import type { CareerPath } from '~/types';

const TOKEN_KEY = 'uni_pilot_auth_token';
const ROADMAP_KEY = 'uni_pilot_roadmap';
const TOPIC_FIELD_ID_KEY = 'uni_pilot_topic_field_id';

export const tokenStorage = {
  getToken: (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken: (token: string): void => {
    if (typeof window === 'undefined') return;
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken: (): void => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(TOKEN_KEY);
  },

  hasToken: (): boolean => {
    return !!tokenStorage.getToken();
  },

  getTopicFieldId: (): number | null => {
    if (typeof window === 'undefined') return null;
    const stored = localStorage.getItem(TOPIC_FIELD_ID_KEY);
    if (!stored) return null;
    const parsed = parseInt(stored, 10);
    return isNaN(parsed) ? null : parsed;
  },

  setTopicFieldId: (id: number): void => {
    if (typeof window === 'undefined') return;
    localStorage.setItem(TOPIC_FIELD_ID_KEY, id.toString());
  },

  removeTopicFieldId: (): void => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(TOPIC_FIELD_ID_KEY);
  },
};