<script lang="ts">
	let { label, value }: { label: string; value: string | number } = $props();
</script>

<div class="border rounded-xl p-4 bg-white"><p class="text-sm text-gray-500">{label}</p><p class="text-2xl font-extrabold">{value}</p></div>
