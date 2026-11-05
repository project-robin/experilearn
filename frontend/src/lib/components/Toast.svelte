<script lang="ts">
	import { toast } from '#lib/stores/auth.svelte';
</script>

{#if $toast}
	<div class="fixed bottom-4 right-4 z-30 rounded-lg px-4 py-2 text-white text-sm shadow-lg {$toast.kind === 'ok' ? 'bg-green-600' : 'bg-red-600'}">{$toast.msg}</div>
{/if}
