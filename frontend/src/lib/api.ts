import { goto } from '$app/navigation';
import { auth, type User } from './stores/auth.svelte';

const API = import.meta.env.VITE_API ?? 'http://localhost:8000';

export async function req<T>(path: string, opts: RequestInit = {}): Promise<T> {
	const token = auth.token;
	const r = await fetch(API + path, {
		...opts,
		headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(opts.headers ?? {}) }
	});
	if (r.status === 401) { auth.logout(); goto('/login'); }
	if (!r.ok) throw new Error(await r.text());
	return r.json();
}

export async function login(email: string, password: string): Promise<User> {
	const r = await req<{ token: string; user: User }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
	auth.set(r.token, r.user);
	return r.user;
}

export async function register(email: string, password: string, name: string, role: string): Promise<User> {
	const r = await req<{ token: string; user: User }>('/auth/register', { method: 'POST', body: JSON.stringify({ email, password, name, role }) });
	auth.set(r.token, r.user);
	return r.user;
}
