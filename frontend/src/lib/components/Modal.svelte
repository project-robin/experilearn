<script lang="ts">
	let { open, onclose, children }: { open: boolean; onclose: () => void; children?: any } = $props();
</script>

{#if open}
	<div class="fixed inset-0 bg-black/50 grid place-items-center z-20 p-4">
		<div class="bg-white rounded-xl max-w-lg w-full p-5 relative">
			<button class="absolute top-3 right-4 text-gray-500" onclick={onclose}>✕</button>
			{@render children?.()}
		</div>
	</div>
{/if}
