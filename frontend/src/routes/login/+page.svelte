<script lang="ts">
	import { login } from '#lib/api';
	import { showToast } from '#lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	let email = $state(''), password = $state(''), loading = $state(false), error = $state('');
	async function submit() {
		loading = true; error = '';
		try { const u = await login(email, password); showToast('Welcome back!'); goto(u.role === 'INSTRUCTOR' ? '/instructor' : u.role === 'ADMIN' ? '/admin' : '/dashboard'); }
		catch { error = 'Invalid credentials.'; }
		loading = false;
	}
</script>

<h1 class="text-2xl font-bold mb-4">Login</h1>
{#if loading}<p>Loading…</p>{/if}
{#if error}<p class="text-red-600 mb-2">{error}</p>{/if}
<form onsubmit={e => { e.preventDefault(); submit(); }} class="flex flex-col gap-2 max-w-sm">
	<input bind:value={email} placeholder="email" class="border rounded p-2 w-full" />
	<input bind:value={password} type="password" placeholder="password" class="border rounded p-2 w-full" />
	<button class="bg-indigo-600 text-white rounded p-2">Login</button>
</form>
<p class="mt-3 text-sm text-gray-600">Try student@experilearn.com / Student@123</p>
