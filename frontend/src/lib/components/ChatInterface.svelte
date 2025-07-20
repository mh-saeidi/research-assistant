<script lang="ts">
	import { chatStore, currentSession } from '$lib/stores/chat';
	import { uiStore } from '$lib/stores/ui';
	import { onMount } from 'svelte';
	import { formatDistanceToNow } from 'date-fns';
	import { Send, Menu, Bot, User, AlertCircle } from 'lucide-svelte';
	import NewResearchForm from './NewResearchForm.svelte';
	import AnalystFeedbackForm from './AnalystFeedbackForm.svelte';

	let messageContainer: HTMLElement;
	let pendingSessionId: string | null = null;
	let showAnalystFeedback = false;
	let analystData: string[] = [];

	$: messages = $chatStore.currentMessages;
	$: isLoading = $chatStore.isLoading;
	$: error = $chatStore.error;

	onMount(() => {
		chatStore.loadSessions();
	});

	function scrollToBottom() {
		if (messageContainer) {
			messageContainer.scrollTop = messageContainer.scrollHeight;
		}
	}

	$: if (messages.length > 0) {
		setTimeout(scrollToBottom, 100);
	}

	function handleNewResearch(event: CustomEvent) {
		const { topic, analystNumber } = event.detail;
		
		chatStore.startNewResearch(topic, analystNumber).then(result => {
			if (result.success) {
				pendingSessionId = result.sessionId;
				analystData = result.analysts;
				showAnalystFeedback = true;
			}
		});
	}

	function handleAnalystFeedback(event: CustomEvent) {
		const { feedback } = event.detail;
		
		if (pendingSessionId) {
			chatStore.submitAnalystFeedback(pendingSessionId, feedback).then(result => {
				if (result.success) {
					showAnalystFeedback = false;
					chatStore.setCurrentSession(pendingSessionId);
					chatStore.loadSessionHistory(pendingSessionId); // Load messages for the completed session
					pendingSessionId = null;
					analystData = [];
					chatStore.loadSessions();
				}
			});
		}
	}

	function formatMessageDate(dateString: string) {
		try {
			return formatDistanceToNow(new Date(dateString), { addSuffix: true });
		} catch {
			return 'Unknown time';
		}
	}

	function clearError() {
		chatStore.clearError();
	}
</script>

<div class="chat-interface">
	<div class="chat-header">
		<button class="menu-button" on:click={() => uiStore.toggleSidebar()}>
			<Menu size={20} />
		</button>
		<div class="header-content">
			{#if $currentSession}
				<h1>{$currentSession.session_name}</h1>
				<p>Research Session</p>
			{:else}
				<h1>AI Research Assistant</h1>
				<p>Start a new research session</p>
			{/if}
		</div>
	</div>

	<div class="chat-content">
		{#if error}
			<div class="error-banner">
				<AlertCircle size={20} />
				<span>{error}</span>
				<button on:click={clearError}>×</button>
			</div>
		{/if}

		{#if showAnalystFeedback}
			<AnalystFeedbackForm 
				{analystData}
				isLoading={$chatStore.isGenerating}
				on:submit={handleAnalystFeedback}
				on:cancel={() => {
					showAnalystFeedback = false;
					pendingSessionId = null;
					analystData = [];
				}}
			/>
		{:else if !$currentSession}
			<NewResearchForm 
				isLoading={$chatStore.isGenerating}
				on:submit={handleNewResearch}
			/>
		{:else}
			<div class="messages-container" bind:this={messageContainer}>
				{#if isLoading && messages.length === 0}
					<div class="loading-state">
						<div class="spinner"></div>
						<p>Loading conversation...</p>
					</div>
				{:else if messages.length === 0}
					<div class="empty-state">
						<Bot size={48} />
						<h3>Research Complete</h3>
						<p>This research session has been completed. The AI has finished analyzing the topic and generated a comprehensive report.</p>
					</div>
				{:else}
					{#each messages as message (message.id)}
						<div class="message-group">
							<!-- User Message -->
							<div class="message user-message">
								<div class="message-avatar">
									<User size={16} />
								</div>
								<div class="message-content">
									<div class="message-header">
										<span class="message-sender">You</span>
										<span class="message-time">{formatMessageDate(message.created_at)}</span>
									</div>
									<div class="message-text">
										{message.message}
									</div>
								</div>
							</div>

							<!-- AI Response -->
							<div class="message ai-message">
								<div class="message-avatar">
									<Bot size={16} />
								</div>
								<div class="message-content">
									<div class="message-header">
										<span class="message-sender">AI Research Assistant</span>
										<span class="message-time">{formatMessageDate(message.created_at)}</span>
									</div>
									<div class="message-text">
										{@html message.response.replace(/\n/g, '<br>')}
									</div>
								</div>
							</div>
						</div>
					{/each}
				{/if}
			</div>
		{/if}
	</div>
</div>

<style>
	.chat-interface {
		flex: 1;
		display: flex;
		flex-direction: column;
		height: 100vh;
		background: white;
	}

	.chat-header {
		display: flex;
		align-items: center;
		padding: 1rem 1.5rem;
		border-bottom: 1px solid #e2e8f0;
		background: white;
		gap: 1rem;
	}

	.menu-button {
		background: none;
		border: none;
		cursor: pointer;
		padding: 8px;
		border-radius: 6px;
		color: #64748b;
		transition: all 0.2s ease;
		display: none;
	}

	.menu-button:hover {
		background: #f1f5f9;
		color: #334155;
	}

	.header-content h1 {
		font-size: 1.25rem;
		font-weight: 600;
		color: #1a202c;
		margin: 0;
		line-height: 1.4;
	}

	.header-content p {
		font-size: 0.875rem;
		color: #64748b;
		margin: 0;
	}

	.chat-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		height: 0; /* allow flex: 1 to take full height */
		min-height: 0;
		overflow: hidden;
	}

	/* Ensure the new research panel is centered vertically and horizontally */
	:global(.new-research-container) {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 0;
	}

	.error-banner {
		background: #fef2f2;
		border: 1px solid #fecaca;
		color: #dc2626;
		padding: 12px 16px;
		display: flex;
		align-items: center;
		gap: 8px;
		margin: 1rem;
		border-radius: 8px;
	}

	.error-banner button {
		background: none;
		border: none;
		color: inherit;
		cursor: pointer;
		font-size: 1.25rem;
		margin-left: auto;
		padding: 0;
		width: 20px;
		height: 20px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.messages-container {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		flex: 1;
		gap: 1rem;
		color: #64748b;
	}

	.spinner {
		width: 32px;
		height: 32px;
		border: 3px solid #e2e8f0;
		border-top: 3px solid #667eea;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		flex: 1;
		text-align: center;
		color: #64748b;
		gap: 1rem;
		padding: 2rem;
	}

	.empty-state :global(svg) {
		color: #cbd5e1;
	}

	.empty-state h3 {
		font-size: 1.25rem;
		font-weight: 600;
		color: #374151;
		margin: 0;
	}

	.empty-state p {
		max-width: 400px;
		line-height: 1.6;
		margin: 0;
	}

	.message-group {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		max-width: 600px;
		margin: 0 auto 1.5rem auto;
	}

	.message {
		display: flex;
		gap: 12px;
		max-width: 100%;
	}

	.message-avatar {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		margin-top: 4px;
	}

	.user-message .message-avatar {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}

	.ai-message .message-avatar {
		background: #f1f5f9;
		color: #64748b;
	}

	.message-content {
		flex: 1;
		min-width: 0;
	}

	.message-header {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 4px;
	}

	.message-sender {
		font-weight: 500;
		font-size: 0.875rem;
		color: #374151;
	}

	.message-time {
		font-size: 0.75rem;
		color: #9ca3af;
	}

	.message-text {
		background: #f8fafc;
		padding: 12px 16px;
		border-radius: 12px;
		line-height: 1.6;
		color: #374151;
		border: 1px solid #e2e8f0;
	}

	.user-message .message-text {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
	}

	.ai-message .message-text {
		background: white;
		border: 1px solid #e2e8f0;
	}

	@media (max-width: 768px) {
		.menu-button {
			display: flex;
		}

		.chat-header {
			padding: 1rem;
		}

		.messages-container {
			padding: 1rem 0.75rem;
		}

		.message {
			gap: 8px;
		}

		.message-group {
			max-width: 100%;
			margin: 0 0 1.5rem 0;
		}

		.message-avatar {
			width: 28px;
			height: 28px;
		}

		.message-text {
			padding: 10px 12px;
			font-size: 0.875rem;
		}
	}
</style>