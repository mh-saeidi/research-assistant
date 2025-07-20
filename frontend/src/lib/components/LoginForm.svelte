<script lang="ts">
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { Eye, EyeOff, Mail, Lock, User } from 'lucide-svelte';

	let isLogin = true;
	let email = '';
	let password = '';
	let firstName = '';
	let lastName = '';
	let showPassword = false;
	let error = '';

	$: isLoading = $authStore.isLoading;

	async function handleSubmit() {
		error = '';
		
		if (!email || !password) {
			error = 'Please fill in all required fields';
			return;
		}

		if (!isLogin && (!firstName || !lastName)) {
			error = 'Please fill in all required fields';
			return;
		}

		let result;
		if (isLogin) {
			result = await authStore.login(email, password);
		} else {
			result = await authStore.register(firstName, lastName, email, password);
		}

		if (result.success) {
			goto('/chat');
		} else {
			error = result.error || 'Authentication failed';
		}
	}

	function toggleMode() {
		isLogin = !isLogin;
		error = '';
	}
</script>

<div class="login-container">
	<div class="login-card">
		<div class="login-header">
			<h1>AI Research Assistant</h1>
			<p>{isLogin ? 'Welcome back' : 'Create your account'}</p>
		</div>

		<form on:submit|preventDefault={handleSubmit} class="login-form">
			{#if !isLogin}
				<div class="form-row">
					<div class="form-group">
						<label for="firstName">First Name</label>
						<div class="input-wrapper">
							<User size={20} />
							<input
								id="firstName"
								type="text"
								bind:value={firstName}
								placeholder="Enter your first name"
								disabled={isLoading}
								required
							/>
						</div>
					</div>
					<div class="form-group">
						<label for="lastName">Last Name</label>
						<div class="input-wrapper">
							<User size={20} />
							<input
								id="lastName"
								type="text"
								bind:value={lastName}
								placeholder="Enter your last name"
								disabled={isLoading}
								required
							/>
						</div>
					</div>
				</div>
			{/if}

			<div class="form-group">
				<label for="email">Email</label>
				<div class="input-wrapper">
					<Mail size={20} />
					<input
						id="email"
						type="email"
						bind:value={email}
						placeholder="Enter your email"
						disabled={isLoading}
						required
					/>
				</div>
			</div>

			<div class="form-group">
				<label for="password">Password</label>
				<div class="input-wrapper">
					<Lock size={20} />
					{#if showPassword}
						<input
							id="password"
							type="text"
							bind:value={password}
							placeholder="Enter your password"
							disabled={isLoading}
							required
						/>
					{:else}
						<input
							id="password"
							type="password"
							bind:value={password}
							placeholder="Enter your password"
							disabled={isLoading}
							required
						/>
					{/if}
					<button
						type="button"
						class="password-toggle"
						on:click={() => showPassword = !showPassword}
						disabled={isLoading}
					>
						{#if showPassword}
							<EyeOff size={20} />
						{:else}
							<Eye size={20} />
						{/if}
					</button>
				</div>
			</div>

			{#if error}
				<div class="error-message">
					{error}
				</div>
			{/if}

			<button type="submit" class="submit-button" disabled={isLoading}>
				{#if isLoading}
					<div class="spinner"></div>
					{isLogin ? 'Signing in...' : 'Creating account...'}
				{:else}
					{isLogin ? 'Sign In' : 'Create Account'}
				{/if}
			</button>
		</form>

		<div class="login-footer">
			<p>
				{isLogin ? "Don't have an account?" : 'Already have an account?'}
				<button type="button" class="link-button" on:click={toggleMode} disabled={isLoading}>
					{isLogin ? 'Sign up' : 'Sign in'}
				</button>
			</p>
		</div>
	</div>
</div>

<style>
	.login-container {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		padding: 1rem;
	}

	.login-card {
		background: white;
		border-radius: 16px;
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
		padding: 2rem;
		width: 100%;
		max-width: 480px;
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

	.login-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.login-header h1 {
		font-size: 2rem;
		font-weight: 700;
		color: #1a202c;
		margin: 0 0 0.5rem 0;
	}

	.login-header p {
		color: #718096;
		margin: 0;
	}

	.login-form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.form-group label {
		font-weight: 500;
		color: #374151;
		font-size: 0.875rem;
	}

	.input-wrapper {
		position: relative;
		display: flex;
		align-items: center;
	}

	.input-wrapper :global(svg) {
		position: absolute;
		left: 12px;
		color: #9ca3af;
		z-index: 1;
	}

	.input-wrapper input {
		width: 100%;
		padding: 12px 44px 12px 44px; /* left icon + right icon */
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 1rem;
		transition: all 0.2s ease;
		background: white;
		box-sizing: border-box;
	}

	.input-wrapper input:focus {
		outline: 2px solid #667eea;
		outline-offset: 2px;
		z-index: 1;
	}

	.input-wrapper input:disabled {
		background: #f9fafb;
		cursor: not-allowed;
	}

	.password-toggle {
		position: absolute;
		right: 16px;
		top: 50%;
		transform: translateY(-50%);
		background: none;
		border: none;
		cursor: pointer;
		color: #9ca3af;
		padding: 0;
		border-radius: 4px;
		transition: color 0.2s ease;
		display: flex;
		align-items: center;
		z-index: 2;
		height: 24px;
		width: 24px;
		justify-content: center;
	}

	.password-toggle:hover:not(:disabled) {
		color: #667eea;
	}

	.password-toggle:disabled {
		cursor: not-allowed;
	}

	.password-toggle:focus {
		outline: none;
		box-shadow: none;
		background: none;
	}

	.error-message {
		background: #fef2f2;
		border: 1px solid #fecaca;
		color: #dc2626;
		padding: 12px;
		border-radius: 8px;
		font-size: 0.875rem;
		text-align: center;
	}

	.submit-button {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		padding: 14px;
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

	.login-footer {
		text-align: center;
		margin-top: 1.5rem;
		padding-top: 1.5rem;
		border-top: 1px solid #e5e7eb;
	}

	.login-footer p {
		color: #718096;
		margin: 0;
	}

	.link-button {
		background: none;
		border: none;
		color: #667eea;
		cursor: pointer;
		font-weight: 500;
		text-decoration: underline;
		margin-left: 4px;
	}

	.link-button:hover:not(:disabled) {
		color: #5a67d8;
	}

	.link-button:disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	@media (max-width: 640px) {
		.login-card {
			padding: 1.5rem;
		}

		.form-row {
			grid-template-columns: 1fr;
		}

		.login-header h1 {
			font-size: 1.75rem;
		}
	}
</style>