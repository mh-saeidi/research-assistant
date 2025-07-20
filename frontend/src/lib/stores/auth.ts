import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface User {
	id: number;
	first_name: string;
	last_name: string;
	email: string;
}

export interface AuthState {
	user: User | null;
	token: string | null;
	isAuthenticated: boolean;
	isLoading: boolean;
}

const initialState: AuthState = {
	user: null,
	token: null,
	isAuthenticated: false,
	isLoading: false
};

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>(initialState);

	return {
		subscribe,
		login: async (email: string, password: string) => {
			update(state => ({ ...state, isLoading: true }));
			
			try {
				const response = await fetch('/api/users/signup', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ email, password })
				});

				if (!response.ok) {
					const error = await response.json();
					throw new Error(error.detail || 'Login failed');
				}

				const data = await response.json();
				const token = data.access_token;

				// Store token in localStorage
				if (browser) {
					localStorage.setItem('auth_token', token);
				}

				// Get user info (you might need to implement this endpoint)
				const userResponse = await fetch('/api/users/me', {
					headers: {
						'Authorization': `Bearer ${token}`
					}
				});

				let user = null;
				if (userResponse.ok) {
					user = await userResponse.json();
				}

				update(state => ({
					...state,
					user,
					token,
					isAuthenticated: true,
					isLoading: false
				}));

				return { success: true };
			} catch (error) {
				update(state => ({ ...state, isLoading: false }));
				return { 
					success: false, 
					error: error instanceof Error ? error.message : 'Login failed' 
				};
			}
		},
		register: async (firstName: string, lastName: string, email: string, password: string) => {
			update(state => ({ ...state, isLoading: true }));
			
			try {
				const response = await fetch('/api/users/signin', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						first_name: firstName,
						last_name: lastName,
						email,
						password
					})
				});

				if (!response.ok) {
					const error = await response.json();
					throw new Error(error.detail || 'Registration failed');
				}

				const data = await response.json();
				const token = data.access_token;

				// Store token in localStorage
				if (browser) {
					localStorage.setItem('auth_token', token);
				}

				const user = {
					id: 1, // You might need to get this from the response
					first_name: firstName,
					last_name: lastName,
					email
				};

				update(state => ({
					...state,
					user,
					token,
					isAuthenticated: true,
					isLoading: false
				}));

				return { success: true };
			} catch (error) {
				update(state => ({ ...state, isLoading: false }));
				return { 
					success: false, 
					error: error instanceof Error ? error.message : 'Registration failed' 
				};
			}
		},
		logout: () => {
			if (browser) {
				localStorage.removeItem('auth_token');
			}
			set(initialState);
		},
		initializeAuth: () => {
			if (browser) {
				const token = localStorage.getItem('auth_token');
				if (token) {
					update(state => ({
						...state,
						token,
						isAuthenticated: true
					}));
				}
			}
		}
	};
}

export const authStore = createAuthStore();