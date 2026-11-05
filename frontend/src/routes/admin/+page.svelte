<script lang="ts">
	import { req } from '#lib/api';
	import { showToast } from '#lib/stores/auth.svelte';
	import StatsCard from '#lib/components/StatsCard.svelte';
	let stats: any = $state(null), users: any[] = $state([]), loading = $state(true), error = $state(''), xml = $state('');
	async function load() {
		try { stats = await req('/analytics/admin'); users = await req('/admin/users'); } catch { error = 'Failed — admin role required.'; }
		loading = false;
	}
	load();
	async function importXml() {
		try { await req('/admin/import/xml', { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: xml }); showToast('Import done'); }
		catch { showToast('Bad XML or no permission', 'err'); }
	}
</script>

<h1 class="text-2xl font-bold mb-4">Admin Dashboard</h1>
{#if loading}<p>Loading…</p>{/if}
{#if error}<p class="text-red-600">{error}</p>{/if}
{#if stats}
	<div class="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-4">
		<StatsCard label="Users" value={stats.total_users} />
		<StatsCard label="Students" value={stats.students} />
		<StatsCard label="Instructors" value={stats.instructors} />
		<StatsCard label="Courses" value={stats.courses} />
		<StatsCard label="Enrollments" value={stats.enrollments} />
	</div>
	<h2 class="font-semibold mb-2">Users</h2>
	{#each users as u}<p class="text-sm border-b py-1">{u.name} · {u.email} · {u.role}</p>{/each}
	<h2 class="font-semibold mt-4 mb-2">Import course (XML)</h2>
	<textarea bind:value={xml} class="border rounded p-2 w-full h-28" placeholder="<course><title>…</title>…</course>"></textarea>
	<button onclick={importXml} class="bg-black text-white rounded px-4 py-2 mt-2">Import</button>
{/if}
