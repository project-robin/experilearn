<script lang="ts">
	import ProgressBar from './ProgressBar.svelte';
	let { course, progress }: { course: any; progress?: number } = $props();
</script>

<a href={`/courses/${course.id}`} class="border rounded-xl p-4 flex flex-col gap-2 bg-white hover:shadow-md transition">
	<div class="flex justify-between text-xs"><span class="bg-indigo-50 text-indigo-700 rounded px-2 py-0.5">{course.category}</span><span class="text-gray-500">{course.difficulty}</span></div>
	<h3 class="font-semibold leading-snug">{course.title}</h3>
	<p class="text-sm text-gray-600 line-clamp-2">{course.description}</p>
	<div class="flex justify-between items-center mt-auto">
		<span class="font-bold">${course.price}</span>
		{#if progress !== undefined}<div class="w-28"><ProgressBar value={progress} /></div>{/if}
	</div>
</a>
