<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { uiStore } from '$lib/stores/ui';
	import ChatSidebar from '$lib/components/ChatSidebar.svelte';
	import ChatInterface from '$lib/components/ChatInterface.svelte';

	onMount(() => {
		// Redirect to login if not authenticated
		if (!$authStore.isAuthenticated) {
			goto('/');
		}
	});

	$: if (!$authStore.isAuthenticated) {
		goto('/');
	}
</script>

<svelte:head>
	<title>AI Research Assistant - Chat</title>
	<meta name="description" content="AI Research Assistant Chat Interface" />
</svelte:head>

{#if $authStore.isAuthenticated}
	<div class="chat-layout">
		{#if $uiStore.sidebarOpen || !$uiStore.isMobile}
			<ChatSidebar />
		{/if}
		<div class="chat-main" class:full-width={!$uiStore.sidebarOpen || $uiStore.isMobile}>
			<ChatInterface />
		</div>
	</div>
{/if}

<style>
	.chat-layout {
		display: flex;
		height: 100vh;
		overflow: hidden;
	}

	.chat-main {
		flex: 1;
		display: flex;
		flex-direction: column;
		margin-left: 320px;
		transition: margin-left 0.3s ease;
	}

	.chat-main.full-width {
		margin-left: 0;
	}

	@media (max-width: 768px) {
		.chat-main {
			margin-left: 0;
		}
	}
</style>