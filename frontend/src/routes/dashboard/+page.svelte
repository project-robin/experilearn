<script lang="ts">
	import { req } from '#lib/api';
	import { auth, showToast } from '#lib/stores/auth.svelte';
	import CourseCard from '#lib/components/CourseCard.svelte';
	import ProgressBar from '#lib/components/ProgressBar.svelte';
	let mine: any[] = $state([]), loading = $state(true), error = $state('');
	req('/enrollments/my').then(r => { mine = r; loading = false; }).catch(() => { error = 'Failed to load — logged in?'; loading = false; });
	async function enroll(cid: number) {
		try { await req(`/enrollments/${cid}`, { method: 'POST' }); showToast('Enrolled!'); location.reload(); }
		catch { showToast('Enroll failed', 'err'); }
	}
</script>

<h1 class="text-2xl font-bold mb-4">My Learning</h1>
{#if !auth.user}<p>Please <a class="underline" href="/login">login</a>.</p>{/if}
{#if loading}<p>Loading…</p>{/if}
{#if error}<p class="text-red-600">{error}</p>{/if}
{#each mine as m}
	<div class="border rounded-xl p-4 mb-3 bg-white">
		<div class="flex justify-between flex-wrap gap-2"><a href={`/courses/${m.course.id}`} class="font-semibold">{m.course.title}</a><span>{m.progress}%</span></div>
		<ProgressBar value={m.progress} />
	</div>
{/each}
