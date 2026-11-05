<script lang="ts">
	import { register } from '#lib/api';
	import { showToast } from '#lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	let email = $state(''), password = $state(''), name = $state(''), role = $state('STUDENT'), loading = $state(false), error = $state('');
	async function submit() {
		loading = true; error = '';
		try { await register(email, password, name, role); showToast('Account created!'); goto('/dashboard'); }
		catch { error = 'Registration failed — email taken?'; }
		loading = false;
	}
</script>

<h1 class="text-2xl font-bold mb-4">Create account</h1>
{#if loading}<p>Loading…</p>{/if}
{#if error}<p class="text-red-600 mb-2">{error}</p>{/if}
<form onsubmit={e => { e.preventDefault(); submit(); }} class="flex flex-col gap-2 max-w-sm">
	<input bind:value={name} placeholder="name" class="border rounded p-2 w-full" />
	<input bind:value={email} placeholder="email" class="border rounded p-2 w-full" />
	<input bind:value={password} type="password" placeholder="password" class="border rounded p-2 w-full" />
	<select bind:value={role} class="border rounded p-2 w-full"><option>STUDENT</option><option>INSTRUCTOR</option></select>
	<button class="bg-indigo-600 text-white rounded p-2">Register</button>
</form>
