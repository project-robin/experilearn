<script lang="ts">
	import { page } from '$app/state';
	import { req } from '#lib/api';
	import { showToast } from '#lib/stores/auth.svelte';
	let m: any = $state(null), loading = $state(true), error = $state('');
	const id = page.params.mid;
	req<any>(`/modules/${id}`).then(r => { m = r; loading = false; }).catch(() => { error = 'Failed to load.'; loading = false; });
	async function complete() {
		try { const r = await req<any>(`/progress/${id}/complete`, { method: 'POST' }); showToast(r.certificate ? 'Complete — certificate issued!' : `Module complete, course ${r.course_progress}%`); }
		catch { showToast('Complete failed', 'err'); }
	}
</script>

{#if loading}<p>Loading…</p>{/if}
{#if error}<p class="text-red-600">{error}</p>{/if}
{#if m}
	<span class="text-xs bg-indigo-50 text-indigo-700 rounded px-2 py-0.5">{m.type}</span>
	<h1 class="text-2xl font-bold mt-2">{m.title}</h1>
	<p class="mt-3 whitespace-pre-wrap">{m.content}</p>
	<button onclick={complete} class="bg-indigo-600 text-white rounded px-4 py-2 mt-4">Mark complete</button>
{/if}
