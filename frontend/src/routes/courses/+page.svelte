<script lang="ts">
	import { req } from '#lib/api';
	import CourseCard from '#lib/components/CourseCard.svelte';
	let q = $state(''), category = $state(''), difficulty = $state(''), items: any[] = $state([]), loading = $state(true), error = $state('');
	async function load() {
		loading = true; error = '';
		try {
			const params = new URLSearchParams({ q, category, difficulty, size: '100' });
			const r = await req<any>(`/courses?${params}`);
			items = r.items;
		} catch { error = 'Failed to load courses.'; }
		loading = false;
	}
	load();
</script>

<h1 class="text-2xl font-bold mb-4">Course Catalog</h1>
<form onsubmit={e => { e.preventDefault(); load(); }} class="flex flex-wrap gap-2 mb-4">
	<input bind:value={q} placeholder="Search…" class="border rounded p-2" />
	<select bind:value={category} class="border rounded p-2"><option value="">All categories</option><option>Science</option><option>Technology</option><option>Robotics</option><option>Business</option><option>Design</option></select>
	<select bind:value={difficulty} class="border rounded p-2"><option value="">All levels</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select>
	<button class="bg-indigo-600 text-white rounded px-4">Search</button>
</form>
{#if loading}<p>Loading…</p>{/if}
{#if error}<p class="text-red-600">{error}</p>{/if}
<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{#each items as c}<CourseCard course={c} />{/each}</div>
