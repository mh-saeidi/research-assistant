import { writable, derived } from 'svelte/store';
import { authStore } from './auth';
import { get } from 'svelte/store';

export interface ChatSession {
	session_id: string;
	session_name: string;
	created_at: string;
}

export interface ChatMessage {
	id: number;
	user_id: number;
	session_id: string;
	session_name: string;
	message: string;
	response: string;
	created_at: string;
}

export interface ChatState {
	sessions: ChatSession[];
	currentSessionId: string | null;
	currentMessages: ChatMessage[];
	isLoading: boolean;
	isGenerating: boolean;
	error: string | null;
}

const initialState: ChatState = {
	sessions: [],
	currentSessionId: null,
	currentMessages: [],
	isLoading: false,
	isGenerating: false,
	error: null
};

function createChatStore() {
	const { subscribe, set, update } = writable<ChatState>(initialState);

	return {
		subscribe,
		loadSessions: async () => {
			const auth = get(authStore);
			if (!auth.token) return;

			update(state => ({ ...state, isLoading: true, error: null }));

			try {
				const response = await fetch('/api/users/get-sessions', {
					headers: {
						'Authorization': `Bearer ${auth.token}`
					}
				});

				if (!response.ok) {
					throw new Error('Failed to load sessions');
				}

				const data = await response.json();
				update(state => ({
					...state,
					sessions: data.sessions || [],
					isLoading: false
				}));
			} catch (error) {
				update(state => ({
					...state,
					isLoading: false,
					error: error instanceof Error ? error.message : 'Failed to load sessions'
				}));
			}
		},
		loadSessionHistory: async (sessionId: string) => {
			const auth = get(authStore);
			if (!auth.token) return;

			update(state => ({ ...state, isLoading: true, error: null }));

			try {
				const response = await fetch(`/api/users/get-session-history/${sessionId}`, {
					headers: {
						'Authorization': `Bearer ${auth.token}`
					}
				});

				if (!response.ok) {
					throw new Error('Failed to load session history');
				}

				const messages = await response.json();
				update(state => ({
					...state,
					currentSessionId: sessionId,
					currentMessages: messages,
					isLoading: false
				}));
			} catch (error) {
				update(state => ({
					...state,
					isLoading: false,
					error: error instanceof Error ? error.message : 'Failed to load session history'
				}));
			}
		},
		startNewResearch: async (topic: string, analystNumber: number) => {
			const auth = get(authStore);
			if (!auth.token) return { success: false, error: 'Not authenticated' };

			update(state => ({ ...state, isGenerating: true, error: null }));

			try {
				const response = await fetch('/api/ai/initiate-research', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						'Authorization': `Bearer ${auth.token}`
					},
					body: JSON.stringify({
						topic,
						analyst_number: analystNumber,
						session_id: null
					})
				});

				if (!response.ok) {
					const error = await response.json();
					throw new Error(error.detail || 'Failed to start research');
				}

				const data = await response.json();
				update(state => ({ ...state, isGenerating: false }));
				
				return { 
					success: true, 
					sessionId: data.session_id,
					analysts: data.resault 
				};
			} catch (error) {
				update(state => ({
					...state,
					isGenerating: false,
					error: error instanceof Error ? error.message : 'Failed to start research'
				}));
				return { 
					success: false, 
					error: error instanceof Error ? error.message : 'Failed to start research' 
				};
			}
		},
		submitAnalystFeedback: async (sessionId: string, feedback: string) => {
			const auth = get(authStore);
			if (!auth.token) return { success: false, error: 'Not authenticated' };

			update(state => ({ ...state, isGenerating: true, error: null }));

			try {
				const response = await fetch('/api/ai/research-analyst-feedback', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						'Authorization': `Bearer ${auth.token}`
					},
					body: JSON.stringify({
						session_id: sessionId,
						feedback
					})
				});

				if (!response.ok) {
					const error = await response.json();
					throw new Error(error.detail || 'Failed to submit feedback');
				}

				const data = await response.json();
				update(state => ({ ...state, isGenerating: false }));
				
				// Reload sessions to get the updated list
				await chatStore.loadSessions();
				
				return { success: true, data };
			} catch (error) {
				update(state => ({
					...state,
					isGenerating: false,
					error: error instanceof Error ? error.message : 'Failed to submit feedback'
				}));
				return { 
					success: false, 
					error: error instanceof Error ? error.message : 'Failed to submit feedback' 
				};
			}
		},
		setCurrentSession: (sessionId: string | null) => {
			update(state => ({ ...state, currentSessionId: sessionId }));
		},
		clearError: () => {
			update(state => ({ ...state, error: null }));
		}
	};
}

export const chatStore = createChatStore();

// Derived store for current session
export const currentSession = derived(
	[chatStore],
	([$chatStore]) => {
		if (!$chatStore.currentSessionId) return null;
		return $chatStore.sessions.find(s => s.session_id === $chatStore.currentSessionId) || null;
	}
);