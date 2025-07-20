<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Users, CheckCircle, MessageCircle, ArrowLeft } from 'lucide-svelte';

	export let analystData: string[] = [];
	export let isLoading = false;

	const dispatch = createEventDispatcher();

	let feedback = '';
	let showCustomFeedback = false;

	function handleApprove() {
		dispatch('submit', { feedback: 'approve' });
	}

	function handleCustomFeedback() {
		if (!feedback.trim()) return;
		dispatch('submit', { feedback: feedback.trim() });
	}

	function handleCancel() {
		dispatch('cancel');
	}

	function toggleCustomFeedback() {
		showCustomFeedback = !showCustomFeedback;
		feedback = '';
	}

	// Parse analyst data into structured format
	$: analysts = parseAnalystData(analystData);

	function parseAnalystData(data: string[]) {
		const analysts = [];
		let currentAnalyst = {};
		
		for (const line of data) {
			if (line.startsWith('Name: ')) {
				if (Object.keys(currentAnalyst).length > 0) {
					analysts.push(currentAnalyst);
				}
				currentAnalyst = { name: line.replace('Name: ', '') };
			} else if (line.startsWith('Affiliation: ')) {
				currentAnalyst.affiliation = line.replace('Affiliation: ', '');
			} else if (line.startsWith('Role: ')) {
				currentAnalyst.role = line.replace('Role: ', '');
			} else if (line.startsWith('Description: ')) {
				currentAnalyst.description = line.replace('Description: ', '');
			} else if (line === '---') {
				// Separator, do nothing
			}
		}
		
		if (Object.keys(currentAnalyst).length > 0) {
			analysts.push(currentAnalyst);
		}
		
		return analysts;
	}
</script>

<div class="feedback-container">
	<div class="feedback-form">
		<div class="form-header">
			<div class="icon-wrapper">
				<Users size={32} />
			</div>
			<h2>Review Research Analysts</h2>
			<p>We've assembled a team of AI analysts for your research. Review their profiles and provide feedback if needed.</p>
		</div>

		<div class="analysts-grid">
			{#each analysts as analyst, index}
				<div class="analyst-card">
					<div class="analyst-header">
						<div class="analyst-avatar">
							{analyst.name?.charAt(0) || 'A'}
						</div>
						<div class="analyst-info">
							<h3>{analyst.name || 'Analyst'}</h3>
							<p class="analyst-role">{analyst.role || 'Research Analyst'}</p>
						</div>
					</div>
					<div class="analyst-details">
						<div class="detail-item">
							<strong>Affiliation:</strong>
							<span>{analyst.affiliation || 'Independent'}</span>
						</div>
						<div class="detail-item">
							<strong>Focus:</strong>
							<span>{analyst.description || 'General research'}</span>
						</div>
					</div>
				</div>
			{/each}
		</div>

		{#if !showCustomFeedback}
			<div class="action-buttons">
				<button 
					class="approve-button" 
					on:click={handleApprove}
					disabled={isLoading}
				>
					{#if isLoading}
						<div class="spinner"></div>
						Starting Research...
					{:else}
						<CheckCircle size={20} />
						Approve & Start Research
					{/if}
				</button>

				<button 
					class="feedback-button" 
					on:click={toggleCustomFeedback}
					disabled={isLoading}
				>
					<MessageCircle size={20} />
					Provide Feedback
				</button>

				<button 
					class="cancel-button" 
					on:click={handleCancel}
					disabled={isLoading}
				>
					<ArrowLeft size={20} />
					Back
				</button>
			</div>
		{:else}
			<div class="custom-feedback">
				<div class="feedback-header">
					<h3>Provide Custom Feedback</h3>
					<p>Describe how you'd like to modify the analyst team or their focus areas.</p>
				</div>

				<div class="form-group">
					<label for="feedback">Your Feedback</label>
					<textarea
						id="feedback"
						bind:value={feedback}
						placeholder="For example: 'Add an analyst focused on economic impacts' or 'Make the team more technical'"
						rows="4"
						disabled={isLoading}
					></textarea>
				</div>

				<div class="feedback-actions">
					<button 
						class="submit-feedback-button" 
						on:click={handleCustomFeedback}
						disabled={isLoading || !feedback.trim()}
					>
						{#if isLoading}
							<div class="spinner"></div>
							Updating Analysts...
						{:else}
							Submit Feedback
						{/if}
					</button>

					<button 
						class="back-button" 
						on:click={toggleCustomFeedback}
						disabled={isLoading}
					>
						Back to Review
					</button>
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.feedback-container {
		flex: 1;
		display: flex;
		align-items: flex-start;
		justify-content: center;
		padding: 2rem;
		background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
		overflow-y: auto;
	}

	.feedback-form {
		background: white;
		border-radius: 16px;
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
		padding: 2rem;
		width: 100%;
		max-width: 800px;
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

	.analysts-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 1.5rem;
		margin-bottom: 2rem;
	}

	.analyst-card {
		background: #f8fafc;
		border: 1px solid #e2e8f0;
		border-radius: 12px;
		padding: 1.5rem;
		transition: all 0.2s ease;
	}

	.analyst-card:hover {
		border-color: #cbd5e1;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
	}

	.analyst-header {
		display: flex;
		align-items: center;
		gap: 12px;
		margin-bottom: 1rem;
	}

	.analyst-avatar {
		width: 48px;
		height: 48px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 600;
		font-size: 1.25rem;
	}

	.analyst-info h3 {
		font-size: 1.125rem;
		font-weight: 600;
		color: #1a202c;
		margin: 0;
	}

	.analyst-role {
		font-size: 0.875rem;
		color: #64748b;
		margin: 0;
	}

	.analyst-details {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.detail-item {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.detail-item strong {
		font-size: 0.875rem;
		color: #374151;
		font-weight: 500;
	}

	.detail-item span {
		font-size: 0.875rem;
		color: #64748b;
		line-height: 1.5;
	}

	.action-buttons {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		align-items: center;
	}

	.approve-button {
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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
		width: 100%;
		max-width: 300px;
	}

	.approve-button:hover:not(:disabled) {
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
	}

	.feedback-button {
		background: #f8fafc;
		color: #475569;
		border: 1px solid #e2e8f0;
		padding: 12px 24px;
		border-radius: 8px;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		width: 100%;
		max-width: 300px;
	}

	.feedback-button:hover:not(:disabled) {
		background: #f1f5f9;
		border-color: #cbd5e1;
	}

	.cancel-button {
		background: none;
		color: #64748b;
		border: none;
		padding: 8px 16px;
		border-radius: 6px;
		font-size: 0.875rem;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 6px;
	}

	.cancel-button:hover:not(:disabled) {
		background: #f1f5f9;
		color: #475569;
	}

	.custom-feedback {
		border-top: 1px solid #e2e8f0;
		padding-top: 2rem;
	}

	.feedback-header {
		margin-bottom: 1.5rem;
	}

	.feedback-header h3 {
		font-size: 1.25rem;
		font-weight: 600;
		color: #1a202c;
		margin: 0 0 0.5rem 0;
	}

	.feedback-header p {
		color: #64748b;
		margin: 0;
		line-height: 1.6;
	}

	.form-group {
		margin-bottom: 1.5rem;
	}

	.form-group label {
		display: block;
		font-weight: 600;
		color: #374151;
		font-size: 0.875rem;
		margin-bottom: 0.5rem;
	}

	.form-group textarea {
		width: 100%;
		padding: 12px 16px;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 1rem;
		font-family: inherit;
		resize: vertical;
		min-height: 100px;
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

	.feedback-actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
	}

	.submit-feedback-button {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		padding: 12px 24px;
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

	.submit-feedback-button:hover:not(:disabled) {
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
	}

	.submit-feedback-button:disabled {
		opacity: 0.7;
		cursor: not-allowed;
		transform: none;
	}

	.back-button {
		background: #f8fafc;
		color: #475569;
		border: 1px solid #e2e8f0;
		padding: 12px 24px;
		border-radius: 8px;
		font-size: 1rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.back-button:hover:not(:disabled) {
		background: #f1f5f9;
		border-color: #cbd5e1;
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

	@media (max-width: 640px) {
		.feedback-container {
			padding: 1rem;
		}

		.feedback-form {
			padding: 1.5rem;
		}

		.analysts-grid {
			grid-template-columns: 1fr;
		}

		.feedback-actions {
			flex-direction: column;
		}

		.action-buttons {
			gap: 0.75rem;
		}
	}
</style>