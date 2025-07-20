import { writable } from 'svelte/store';

export interface UIState {
	sidebarOpen: boolean;
	theme: 'light' | 'dark';
	isMobile: boolean;
}

const initialState: UIState = {
	sidebarOpen: true,
	theme: 'light',
	isMobile: false
};

function createUIStore() {
	const { subscribe, set, update } = writable<UIState>(initialState);

	return {
		subscribe,
		toggleSidebar: () => {
			update(state => ({ ...state, sidebarOpen: !state.sidebarOpen }));
		},
		setSidebarOpen: (open: boolean) => {
			update(state => ({ ...state, sidebarOpen: open }));
		},
		toggleTheme: () => {
			update(state => ({ 
				...state, 
				theme: state.theme === 'light' ? 'dark' : 'light' 
			}));
		},
		setMobile: (isMobile: boolean) => {
			update(state => ({ ...state, isMobile }));
		}
	};
}

export const uiStore = createUIStore();