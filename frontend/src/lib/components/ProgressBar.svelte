<script lang="ts">
	let { value }: { value: number } = $props();
</script>

<div class="h-2.5 bg-gray-200 rounded-full overflow-hidden"><div class="h-full bg-indigo-600 rounded-full" style={`width:${Math.min(100, Math.max(0, value))}%`}></div></div>
