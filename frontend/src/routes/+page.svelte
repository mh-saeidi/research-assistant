<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import LoginForm from '$lib/components/LoginForm.svelte';

	onMount(() => {
		// Redirect to chat if already authenticated
		if ($authStore.isAuthenticated) {
			goto('/chat');
		}
	});

	$: if ($authStore.isAuthenticated) {
		goto('/chat');
	}
</script>

<svelte:head>
	<title>AI Research Assistant - Login</title>
	<meta name="description" content="Login to AI Research Assistant" />
</svelte:head>

<LoginForm />