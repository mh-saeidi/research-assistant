<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Search, Users, Lightbulb } from 'lucide-svelte';

	export let isLoading = false;

	const dispatch = createEventDispatcher();

	let topic = '';
	let analystNumber = 3;

	function handleSubmit() {
		if (!topic.trim()) return;
		
		dispatch('submit', {
			topic: topic.trim(),
			analystNumber
		});
	}

	const suggestions = [
		'Climate change impact on agriculture',
		'Artificial intelligence in healthcare',
		'Renewable energy adoption trends',
		'Future of remote work',
		'Cryptocurrency market analysis',
		'Space exploration technologies'
	];

	function selectSuggestion(suggestion: string) {
		topic = suggestion;
	}
</script>

<div class="new-research-container">
	<div class="research-form">
		<div class="form-header">
			<div class="icon-wrapper">
				<Search size={32} />
			</div>
			<h2>Start New Research</h2>
			<p>Let our AI analysts research any topic for you. Provide a topic and choose how many analysts you'd like to work on it.</p>
		</div>

		<form on:submit|preventDefault={handleSubmit} class="form-content">
			<div class="form-group">
				<label for="topic">Research Topic</label>
				<textarea
					id="topic"
					bind:value={topic}
					placeholder="Enter the topic you'd like to research..."
					rows="3"
					disabled={isLoading}
					required
				></textarea>
			</div>

			<div class="form-group">
				<label for="analysts">Number of Analysts</label>
				<div class="analyst-selector">
					<Users size={20} />
					<select id="analysts" bind:value={analystNumber} disabled={isLoading}>
						<option value={1}>1 Analyst</option>
						<option value={2}>2 Analysts</option>
						<option value={3}>3 Analysts</option>
						<option value={4}>4 Analysts</option>
						<option value={5}>5 Analysts</option>
					</select>
				</div>
				<p class="form-help">More analysts provide diverse perspectives but take longer to complete.</p>
			</div>

			<button type="submit" class="submit-button" disabled={isLoading || !topic.trim()}>
				{#if isLoading}
					<div class="spinner"></div>
					Generating Analysts...
				{:else}
					<Search size={20} />
					Start Research
				{/if}
			</button>
		</form>

		<div class="suggestions">
			<div class="suggestions-header">
				<Lightbulb size={16} />
				<span>Suggested Topics</span>
			</div>
			<div class="suggestions-grid">
				{#each suggestions as suggestion}
					<button 
						class="suggestion-chip"
						on:click={() => selectSuggestion(suggestion)}
						disabled={isLoading}
					>
						{suggestion}
					</button>
				{/each}
			</div>
		</div>
	</div>
</div>

<style>
	.new-research-container {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
	}

	.research-form {
		background: white;
		border-radius: 16px;
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
		padding: 2rem;
		width: 100%;
		max-width: 600px;
		animation: slideUp 0.5s ease-out;
	}

	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.form-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.icon-wrapper {
		width: 64px;
		height: 64px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		margin: 0 auto 1rem auto;
		color: white;
	}

	.form-header h2 {
		font-size: 1.75rem;
		font-weight: 700;
		color: #1a202c;
		margin: 0 0 0.5rem 0;
	}

	.form-header p {
		color: #64748b;
		line-height: 1.6;
		margin: 0;
	}

	.form-content {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		margin-bottom: 2rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.form-group label {
		font-weight: 600;
		color: #374151;
		font-size: 0.875rem;
	}

	.form-group textarea {
		padding: 12px 16px;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 1rem;
		font-family: inherit;
		resize: vertical;
		min-height: 80px;
		transition: all 0.2s ease;
	}

	.form-group textarea:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	.form-group textarea:disabled {
		background: #f9fafb;
		cursor: not-allowed;
	}

	.analyst-selector {
		position: relative;
		display: flex;
		align-items: center;
	}

	.analyst-selector :global(svg) {
		position: absolute;
		left: 12px;
		color: #9ca3af;
		z-index: 1;
	}

	.analyst-selector select {
		width: 100%;
		padding: 12px 16px 12px 44px;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 1rem;
		background: white;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.analyst-selector select:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
	}

	.analyst-selector select:disabled {
		background: #f9fafb;
		cursor: not-allowed;
	}

	.form-help {
		font-size: 0.75rem;
		color: #9ca3af;
		margin: 0;
		line-height: 1.4;
	}

	.submit-button {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		padding: 14px 24px;
		border-radius: 8px;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
	}

	.submit-button:hover:not(:disabled) {
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
	}

	.submit-button:disabled {
		opacity: 0.7;
		cursor: not-allowed;
		transform: none;
	}

	.spinner {
		width: 20px;
		height: 20px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top: 2px solid white;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.suggestions {
		border-top: 1px solid #e5e7eb;
		padding-top: 1.5rem;
	}

	.suggestions-header {
		display: flex;
		align-items: center;
		gap: 6px;
		margin-bottom: 1rem;
		color: #64748b;
		font-size: 0.875rem;
		font-weight: 500;
	}

	.suggestions-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 8px;
	}

	.suggestion-chip {
		background: #f8fafc;
		border: 1px solid #e2e8f0;
		color: #475569;
		padding: 8px 12px;
		border-radius: 20px;
		font-size: 0.875rem;
		cursor: pointer;
		transition: all 0.2s ease;
		text-align: left;
	}

	.suggestion-chip:hover:not(:disabled) {
		background: #e2e8f0;
		border-color: #cbd5e1;
		transform: translateY(-1px);
	}

	.suggestion-chip:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	@media (max-width: 640px) {
		.new-research-container {
			padding: 1rem;
		}

		.research-form {
			padding: 1.5rem;
		}

		.form-header h2 {
			font-size: 1.5rem;
		}

		.suggestions-grid {
			grid-template-columns: 1fr;
		}
	}
</style>