<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { github_auth_enabled, google_auth_enabled } from '$lib/config';
	import { getLocalization } from '$lib/i18n';

	export let session_data = {};
	export let step;

	const { t } = getLocalization();
	let email = '';
	let emailEmpty = true;
	let isSubmitting = false;

	$: emailEmpty = email === '';
	const start_login = async (): Promise<void> => {
		if (emailEmpty) {
			return;
		}
		isSubmitting = true;
		const res = await fetch('/api/v1/login/start', {
			method: 'post',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ email: email })
		});
		session_data = await res.json();
		step = 1;
	};
</script>

<div class="px-6 py-4">
	<h2 class="text-3xl font-bold text-center text-gray-700 dark:text-white">ClassQuiz</h2>

	<h3 class="mt-1 text-xl font-medium text-center text-gray-600 dark:text-gray-200">
		{$t('login_page.welcome_back')}
	</h3>

	<p class="mt-1 text-center text-gray-500 dark:text-gray-400">
		{$t('login_page.login_or_create_account')}
	</p>

	<form on:submit|preventDefault={start_login}>
		<div class="w-full mt-4">
			<div class="dark:bg-gray-800 bg-white p-4 rounded-lg">
				<div class="relative bg-inherit w-full">
					<input
						id="email"
						bind:value={email}
						name="email"
						type="text"
						class="w-full peer bg-transparent h-10 rounded-lg text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600"
						placeholder={$t('login_page.email_or_username')}
						autocomplete="email"
					/>
					<label
						for="email"
						class="absolute cursor-text left-0 -top-3 text-sm text-gray-700 dark:text-white bg-inherit mx-1 px-1 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:top-2 peer-focus:-top-3 peer-focus:text-sky-600 peer-focus:text-sm transition-all"
					>
						{$t('login_page.email_or_username')}
					</label>
				</div>
			</div>
			<div class="flex items-center justify-between mt-4">
				<a
					href="/account/reset-password"
					class="text-sm text-gray-600 dark:text-gray-200 hover:text-gray-500"
					>{$t('register_page.forgot_password?')}</a
				>

				<button
					class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
					disabled={emailEmpty}
					type="submit"
				>
					{#if isSubmitting}
						<svg class="h-4 w-4 animate-spin mx-auto" viewBox="3 3 18 18">
							<path
								class="fill-black"
								d="M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z"
							/>
							<path
								class="fill-blue-100"
								d="M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z"
							/>
						</svg>
					{:else}
						{$t('words.continue')}
					{/if}
				</button>
			</div>
			{#if google_auth_enabled}
				<div class="flex items-center justify-center pt-4">
					<a
						href="/api/v1/users/oauth/google/login"
						class="inline-flex w-fit p-1 rounded-lg border-gray-500 border border-2 hover:bg-[#4285F4] transition"
						>Google Login

						<svg
							class="h-6 w-6 ml-4 dark:fill-gray-300"
							role="img"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
							><title> Google</title>
							<path
								d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"
							/>
						</svg>
					</a>
				</div>
			{/if}
			{#if github_auth_enabled}
				<div class="flex items-center w-full justify-center pt-4">
					<a
						href="/api/v1/users/oauth/github/login"
						class="inline-flex w-fit p-1 rounded-lg border-gray-500 border border-2 hover:bg-[#181717] transition hover:text-white group"
						>GitHub Login
						<svg
							class="h-6 w-6 ml-4 dark:fill-gray-300 group-hover:fill-white transition"
							role="img"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
							><title> GitHub</title>
							<path
								d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
							/>
						</svg>
					</a>
				</div>
			{/if}
		</div>
	</form>
</div>

<div class="flex items-center justify-center py-4 text-center bg-gray-50 dark:bg-gray-700">
	<span class="text-sm text-gray-600 dark:text-gray-200"
		>{$t('login_page.already_have_account')}
	</span>

	<a
		href="/account/register"
		class="mx-2 text-sm font-bold text-blue-500 dark:text-blue-400 hover:underline"
		>{$t('words.register')}</a
	>
</div>
