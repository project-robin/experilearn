<script lang="ts">
	import { req } from '#lib/api';
	import { showToast } from '#lib/stores/auth.svelte';
	import StatsCard from '#lib/components/StatsCard.svelte';
	import Modal from '#lib/components/Modal.svelte';
	let stats: any = $state(null), courses: any[] = $state([]), loading = $state(true), error = $state('');
	let open = $state(false), form: any = $state({ title: '', description: '', category: 'Technology', difficulty: 'Beginner', price: 0, thumbnail: '' });
	let modForm: any = $state({ course_id: 0, title: '', type: 'Video Lesson', content: '' });
	async function load() {
		try { stats = await req('/analytics/instructor'); courses = (await req<any>('/courses?size=100')).items; } catch { error = 'Failed — instructor role required.'; }
		loading = false;
	}
	load();
	async function create() {
		try { await req('/courses', { method: 'POST', body: JSON.stringify(form) }); showToast('Course created'); open = false; load(); } catch { showToast('Failed', 'err'); }
	}
	async function addModule() {
		try { await req(`/courses/${modForm.course_id}/modules`, { method: 'POST', body: JSON.stringify(modForm) }); showToast('Module added'); } catch { showToast('Failed', 'err'); }
	}
</script>

<h1 class="text-2xl font-bold mb-4">Instructor Dashboard</h1>
{#if loading}<p>Loading…</p>{/if}
{#if error}<p class="text-red-600">{error}</p>{/if}
{#if stats}
	<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
		<StatsCard label="Total students" value={stats.total_students} />
		<StatsCard label="Enrollments" value={stats.total_enrollments} />
		<StatsCard label="Avg progress" value={`${stats.avg_progress}%`} />
		<StatsCard label="Courses" value={stats.per_course.length} />
	</div>
	<h2 class="font-semibold mb-2">Enrollments per course</h2>
	{#each stats.per_course as p}<p class="text-sm">{p.title}: {p.enrollments} students, avg {p.avg_progress}%</p>{/each}
	<button onclick={() => open = true} class="bg-indigo-600 text-white rounded px-4 py-2 mt-4">New course</button>
	<form onsubmit={e => { e.preventDefault(); addModule(); }} class="mt-4 border rounded p-3 flex flex-col gap-2 max-w-md">
		<strong>Add module</strong>
		<select bind:value={modForm.course_id} class="border rounded p-2">{#each courses as c}<option value={c.id}>{c.title}</option>{/each}</select>
		<input bind:value={modForm.title} placeholder="Module title" class="border rounded p-2" />
		<select bind:value={modForm.type} class="border rounded p-2"><option>Virtual Lab</option><option>Simulation</option><option>Case Study</option><option>DIY Project</option><option>Video Lesson</option><option>Quiz</option></select>
		<textarea bind:value={modForm.content} placeholder="Content" class="border rounded p-2"></textarea>
		<button class="bg-black text-white rounded p-2">Add module</button>
	</form>
{/if}
<Modal {open} onclose={() => open = false}>
	<h2 class="font-bold mb-2">New course</h2>
	<form onsubmit={e => { e.preventDefault(); create(); }} class="flex flex-col gap-2">
		<input bind:value={form.title} placeholder="Title" class="border rounded p-2" required />
		<input bind:value={form.description} placeholder="Description" class="border rounded p-2" />
		<select bind:value={form.category} class="border rounded p-2"><option>Science</option><option>Technology</option><option>Robotics</option><option>Business</option><option>Design</option></select>
		<select bind:value={form.difficulty} class="border rounded p-2"><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select>
		<input bind:value={form.price} type="number" min="0" class="border rounded p-2" />
		<button class="bg-indigo-600 text-white rounded p-2">Create</button>
	</form>
</Modal>
