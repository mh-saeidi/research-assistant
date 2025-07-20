<script lang="ts">
	import { chatStore, currentSession } from '$lib/stores/chat';
	import { uiStore } from '$lib/stores/ui';
	import { authStore } from '$lib/stores/auth';
	import { formatDistanceToNow } from 'date-fns';
	import { Plus, Search, MessageSquare, X, Menu, LogOut } from 'lucide-svelte';

	let searchQuery = '';

	$: sessions = $chatStore.sessions;
	$: filteredSessions = sessions.filter(session =>
		session.session_name.toLowerCase().includes(searchQuery.toLowerCase())
	);

	function selectSession(sessionId: string) {
		chatStore.loadSessionHistory(sessionId);
		if ($uiStore.isMobile) {
			uiStore.setSidebarOpen(false);
		}
	}

	function handleNewChat() {
		chatStore.setCurrentSession(null);
		if ($uiStore.isMobile) {
			uiStore.setSidebarOpen(false);
		}
	}

	function handleLogout() {
		authStore.logout();
	}

	function formatDate(dateString: string) {
		try {
			return formatDistanceToNow(new Date(dateString), { addSuffix: true });
		} catch {
			return 'Unknown';
		}
	}
</script>

<aside class="sidebar" class:open={$uiStore.sidebarOpen}>
	<div class="sidebar-header">
		<div class="header-content">
			<h2>Research Sessions</h2>
			{#if $uiStore.isMobile}
				<button class="close-button" on:click={() => uiStore.setSidebarOpen(false)}>
					<X size={20} />
				</button>
			{/if}
		</div>
		
		<button class="new-chat-button" on:click={handleNewChat}>
			<Plus size={20} />
			New Research
		</button>
	</div>

	<div class="search-container">
		<div class="search-wrapper">
			<Search size={16} />
			<input
				type="text"
				placeholder="Search sessions..."
				bind:value={searchQuery}
			/>
		</div>
	</div>

	<div class="sessions-list">
		{#if $chatStore.isLoading}
			<div class="loading-state">
				<div class="spinner"></div>
				<p>Loading sessions...</p>
			</div>
		{:else if filteredSessions.length === 0}
			<div class="empty-state">
				{#if searchQuery}
					<p>No sessions found matching "{searchQuery}"</p>
				{:else}
					<MessageSquare size={48} />
					<p>No research sessions yet</p>
					<span>Start a new research session to begin</span>
				{/if}
			</div>
		{:else}
			{#each filteredSessions as session (session.session_id)}
				<button
					class="session-item"
					class:active={$currentSession?.session_id === session.session_id}
					on:click={() => selectSession(session.session_id)}
				>
					<div class="session-content">
						<h3>{session.session_name}</h3>
						<p class="session-date">{formatDate(session.created_at)}</p>
					</div>
				</button>
			{/each}
		{/if}
	</div>

	<div class="sidebar-footer">
		{#if $authStore.user}
			<div class="user-info">
				<div class="user-avatar">
					{$authStore.user.first_name.charAt(0)}{$authStore.user.last_name.charAt(0)}
				</div>
				<div class="user-details">
					<p class="user-name">{$authStore.user.first_name} {$authStore.user.last_name}</p>
					<p class="user-email">{$authStore.user.email}</p>
				</div>
			</div>
		{/if}
		
		<button class="logout-button" on:click={handleLogout}>
			<LogOut size={16} />
			Logout
		</button>
	</div>
</aside>

{#if $uiStore.isMobile && $uiStore.sidebarOpen}
	<div class="sidebar-overlay" on:click={() => uiStore.setSidebarOpen(false)}></div>
{/if}

<style>
	.sidebar {
		width: 320px;
		height: 100vh;
		background: #f8fafc;
		border-right: 1px solid #e2e8f0;
		display: flex;
		flex-direction: column;
		position: fixed;
		left: 0;
		top: 0;
		z-index: 100;
		transform: translateX(-100%);
		transition: transform 0.3s ease;
		flex-shrink: 0;
	}

	.sidebar.open {
		transform: translateX(0);
	}

	.sidebar-header {
		padding: 1.5rem;
		border-bottom: 1px solid #e2e8f0;
		background: white;
	}

	.header-content {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.header-content h2 {
		font-size: 1.25rem;
		font-weight: 600;
		color: #1a202c;
		margin: 0;
	}

	.close-button {
		background: none;
		border: none;
		cursor: pointer;
		padding: 4px;
		border-radius: 4px;
		color: #64748b;
		transition: all 0.2s ease;
	}

	.close-button:hover {
		background: #f1f5f9;
		color: #334155;
	}

	.new-chat-button {
		width: 100%;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		padding: 12px 16px;
		border-radius: 8px;
		font-weight: 500;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		transition: all 0.2s ease;
	}

	.new-chat-button:hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
	}

	.search-container {
		padding: 1rem 1.5rem;
		background: white;
		border-bottom: 1px solid #e2e8f0;
	}

	.search-wrapper {
		position: relative;
		display: flex;
		align-items: center;
	}

	.search-wrapper :global(svg) {
		position: absolute;
		left: 12px;
		color: #9ca3af;
		z-index: 1;
	}

	.search-wrapper input {
		width: 100%;
		padding: 10px 12px 10px 36px;
		border: 1px solid #e2e8f0;
		border-radius: 6px;
		font-size: 0.875rem;
		background: #f8fafc;
		transition: all 0.2s ease;
	}

	.search-wrapper input:focus {
		outline: none;
		border-color: #667eea;
		background: white;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	.sessions-list {
		flex: 1;
		overflow-y: auto;
		padding: 0.5rem;
	}

	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		color: #64748b;
		gap: 1rem;
	}

	.spinner {
		width: 24px;
		height: 24px;
		border: 2px solid #e2e8f0;
		border-top: 2px solid #667eea;
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
		padding: 2rem;
		text-align: center;
		color: #64748b;
		gap: 0.5rem;
	}

	.empty-state :global(svg) {
		color: #cbd5e1;
		margin-bottom: 0.5rem;
	}

	.empty-state p {
		font-weight: 500;
		margin: 0;
	}

	.empty-state span {
		font-size: 0.875rem;
		margin: 0;
	}

	.session-item {
		width: 100%;
		background: none;
		border: none;
		padding: 12px;
		border-radius: 8px;
		cursor: pointer;
		text-align: left;
		transition: all 0.2s ease;
		margin-bottom: 4px;
	}

	.session-item:hover {
		background: #f1f5f9;
	}

	.session-item.active {
		background: #e0e7ff;
		border: 1px solid #c7d2fe;
	}

	.session-content h3 {
		font-size: 0.875rem;
		font-weight: 500;
		color: #1a202c;
		margin: 0 0 4px 0;
		line-height: 1.4;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.session-date {
		font-size: 0.75rem;
		color: #64748b;
		margin: 0;
	}

	.sidebar-footer {
		padding: 1rem 1.5rem;
		border-top: 1px solid #e2e8f0;
		background: white;
	}

	.user-info {
		display: flex;
		align-items: center;
		gap: 12px;
		margin-bottom: 1rem;
	}

	.user-avatar {
		width: 40px;
		height: 40px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 600;
		font-size: 0.875rem;
	}

	.user-details {
		flex: 1;
		min-width: 0;
	}

	.user-name {
		font-size: 0.875rem;
		font-weight: 500;
		color: #1a202c;
		margin: 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.user-email {
		font-size: 0.75rem;
		color: #64748b;
		margin: 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.logout-button {
		width: 100%;
		background: #f8fafc;
		border: 1px solid #e2e8f0;
		color: #64748b;
		padding: 8px 12px;
		border-radius: 6px;
		font-size: 0.875rem;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 6px;
		transition: all 0.2s ease;
	}

	.logout-button:hover {
		background: #f1f5f9;
		border-color: #cbd5e1;
		color: #475569;
	}

	.sidebar-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		z-index: 99;
	}

	@media (min-width: 768px) {
		.sidebar {
			position: relative;
			transform: translateX(0);
		}

		.close-button {
			display: none;
		}
	}
</style>