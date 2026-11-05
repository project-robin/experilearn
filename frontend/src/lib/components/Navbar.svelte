<script lang="ts">
	import { auth } from '#lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	function logout() { auth.logout(); goto('/login'); }
</script>

<header class="border-b bg-white/80 backdrop-blur sticky top-0 z-10">
	<nav class="max-w-6xl mx-auto flex items-center gap-4 px-4 py-3 text-sm">
		<a href="/" class="font-extrabold text-lg tracking-tight">Experi<span class="text-indigo-600">Learn</span></a>
		<a href="/courses" class="hover:text-indigo-600">Catalog</a>
		{#if auth.user}
			{#if auth.user.role === 'STUDENT'}<a href="/dashboard" class="hover:text-indigo-600">My Learning</a>{/if}
			{#if auth.user.role !== 'STUDENT'}<a href="/instructor" class="hover:text-indigo-600">Instructor</a>{/if}
			{#if auth.user.role === 'ADMIN'}<a href="/admin" class="hover:text-indigo-600">Admin</a>{/if}
		{/if}
		<span class="flex-1"></span>
		{#if auth.user}
			<span class="text-gray-500 hidden sm:inline">{auth.user.name || auth.user.email} · {auth.user.role}</span>
			<button onclick={logout} class="border rounded px-3 py-1">Logout</button>
		{:else}
			<a href="/login" class="hover:text-indigo-600">Login</a>
			<a href="/register" class="bg-indigo-600 text-white rounded px-3 py-1">Sign up</a>
		{/if}
	</nav>
</header>
