<script lang="ts">
	import { page } from '$app/state';
	import { req } from '#lib/api';
	let quiz: any = $state(null), answers: number[] = $state([]), loading = $state(true), error = $state(''), result: any = $state(null), left = $state(300), timer: any = null;
	const id = page.params.mid;
	req<any>(`/modules/${id}/quiz`).then(r => { quiz = r; answers = r.questions.map(() => -1); loading = false; timer = setInterval(() => { if (left > 0) left--; }, 1000); })
		.catch(() => { error = 'No quiz for this module.'; loading = false; });
	async function submit() {
		clearInterval(timer);
		try { result = await req(`/modules/${id}/quiz/attempt`, { method: 'POST', body: JSON.stringify({ answers }) }); } catch { error = 'Submit failed.'; }
	}
</script>

{#if loading}<p>Loading…</p>{/if}
{#if error}<p class="text-red-600">{error}</p>{/if}
{#if quiz}
	<h1 class="text-2xl font-bold">{quiz.title}</h1>
	<p class="text-sm text-gray-600">Time left: {Math.floor(left / 60)}:{String(left % 60).padStart(2, '0')}</p>
	{#each quiz.questions as q, i}
		<fieldset class="border rounded p-3 my-3"><legend class="text-sm font-medium">{q.q}</legend>
			{#each q.options as opt, j}<label class="block text-sm"><input type="radio" name={`q${i}`} checked={answers[i] === j} onchange={() => answers[i] = j} /> {opt}</label>{/each}
		</fieldset>
	{/each}
	<button onclick={submit} class="bg-indigo-600 text-white rounded px-4 py-2">Submit</button>
	{#if result}<p class="mt-3 font-bold">Score: {result.score}% ({result.correct}/{result.total}) — {result.passed ? 'Passed ✓' : 'Not passed'}</p>{/if}
{/if}
