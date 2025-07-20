<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { uiStore } from '$lib/stores/ui';
	import '../app.css';

	onMount(() => {
		// Initialize auth from localStorage
		authStore.initializeAuth();

		// Handle responsive design
		function handleResize() {
			uiStore.setMobile(window.innerWidth < 768);
			if (window.innerWidth >= 768) {
				uiStore.setSidebarOpen(true);
			}
		}

		handleResize();
		window.addEventListener('resize', handleResize);

		return () => {
			window.removeEventListener('resize', handleResize);
		};
	});
</script>

<main>
	<slot />
</main>

<style>
	main {
		height: 100vh;
		overflow: hidden;
	}
</style>