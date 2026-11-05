<script lang="ts">
	import { page } from '$app/state';
	import { req } from '#lib/api';
	import { auth, showToast } from '#lib/stores/auth.svelte';
	import ProgressBar from '#lib/components/ProgressBar.svelte';
	let course: any = $state(null), modules: any[] = $state([]), loading = $state(true), error = $state(''), pct: number | null = $state(null);
	const id = page.params.id;
	Promise.all([req<any>(`/courses/${id}`), req<any[]>(`/courses/${id}/modules`)])
		.then(([c, m]) => { course = c; modules = m; loading = false; })
		.catch(() => { error = 'Failed to load.'; loading = false; });
	if (auth.user) req<any>(`/progress/${id}`).then(r => pct = r.progress).catch(() => {});
	async function enroll() {
		try { await req(`/enrollments/${id}`, { method: 'POST' }); showToast('Enrolled!'); } catch { showToast('Enroll failed', 'err'); }
	}
</script>

{#if loading}<p>Loading…</p>{/if}
{#if error}<p class="text-red-600">{error}</p>{/if}
{#if course}
	<h1 class="text-2xl font-bold">{course.title}</h1>
	<p class="text-gray-600 mt-1">{course.description}</p>
	<p class="text-sm mt-2">${course.price} · {course.category} · {course.difficulty}</p>
	{#if pct !== null}<div class="my-3"><p class="text-sm">Your progress: {pct}%</p><ProgressBar value={pct} /></div>{/if}
	{#if auth.user}<button onclick={enroll} class="bg-indigo-600 text-white rounded px-4 py-2 my-3">Enroll</button>{/if}
	<h2 class="font-semibold mt-4">Modules</h2>
	<ol class="mt-2 flex flex-col gap-2">{#each modules as m}
		<li class="border rounded p-3">
			<span class="text-xs bg-gray-100 rounded px-2 py-0.5">{m.type}</span>
			<a class="font-medium" href={`/learn/${m.id}`}>{m.title}</a>
			{#if m.type === 'Quiz'}<a class="ml-2 underline text-sm" href={`/quiz/${m.id}`}>Take quiz</a>{/if}
		</li>{/each}</ol>
{/if}
