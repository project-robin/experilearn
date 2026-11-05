import { writable } from 'svelte/store';

export type User = { id: number; email: string; name: string; role: string };

const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('el_token') : null;
const storedUser = typeof localStorage !== 'undefined' ? localStorage.getItem('el_user') : null;

class AuthStore {
	token: string | null = $state(stored);
	user: User | null = $state(storedUser ? JSON.parse(storedUser) : null);

	set(token: string, user: User) {
		this.token = token; this.user = user;
		localStorage.setItem('el_token', token);
		localStorage.setItem('el_user', JSON.stringify(user));
	}
	logout() {
		this.token = null; this.user = null;
		localStorage.removeItem('el_token');
		localStorage.removeItem('el_user');
	}
}

export const auth = new AuthStore();
export const toast = writable<{ msg: string; kind: 'ok' | 'err' } | null>(null);
export function showToast(msg: string, kind: 'ok' | 'err' = 'ok') {
	toast.set({ msg, kind });
	setTimeout(() => toast.set(null), 3500);
}
