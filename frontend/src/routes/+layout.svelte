<script lang="ts">
	import '../app.css';
	import type { LayoutProps } from './$types';
	import Navbar from '#lib/components/Navbar.svelte';
	import Toast from '#lib/components/Toast.svelte';
	let { children }: LayoutProps = $props();
</script>

<Navbar />
<main class="max-w-6xl mx-auto px-4 py-6">{@render children()}</main>
<Toast />
