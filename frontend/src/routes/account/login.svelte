<script context="module" lang="ts">
	export async function load({ session, url }) {
		const verified = url.searchParams.get('verified');
		const returnTo =
			url.searchParams.get('returnTo') !== null
				? url.searchParams.get('returnTo')
				: '/overview';
		if (session.authenticated) {
			return {
				status: 302,
				redirect: returnTo
			};
		}
		return {
			status: 200,
			props: {
				verified: verified !== null
			}
		};
	}
</script>

<script lang="ts">
	import * as Sentry from '@sentry/browser';
	import { navbarVisible } from '$lib/stores';
	import { browser } from '$app/env';
	import Cookies from 'js-cookie';
	import { getLocalization } from '$lib/i18n';
	import Footer from '$lib/footer.svelte';
	import { google_auth_enabled, github_auth_enabled } from '$lib/config';

	const { t } = getLocalization();

	navbarVisible.set(true);

	export let verified: boolean;

	let loginData = {
		email: '',
		password: ''
	};
	let emailEmpty = true;
	let passwordEmpty = true;
	let responseData = {
		open: false,
		data: ''
	};
	let inputValid = false;
	let isSubmitting = false;

	$: emailEmpty = loginData.email === '';
	$: passwordEmpty = loginData.password === '';
	$: inputValid = !emailEmpty && !passwordEmpty;

	const reloadWindow = () => {
		const expireIn60Sec = new Date(new Date().getTime() + 60 * 1000);
		if (Cookies.get('reload') === undefined) {
			Cookies.set('reload', '1', { expires: expireIn60Sec });
		} else {
			const cookie: string = Cookies.get('reload');
			if (parseInt(cookie) >= 3) {
				if (import.meta.env.VITE_SENTRY !== null) {
					Sentry.captureException(new Error('Reload loop'));
				}
				fetch('/api/v1/users/logout').then();
				Cookies.remove('reload');
			}
			Cookies.set('reload', String(parseInt(cookie) + 1), { expires: expireIn60Sec });
		}
		window.location.reload();
	};

	const checkRememberMe = async () => {
		const res = await fetch('/api/v1/users/token/rememberme');
		if (res.status === 200) {
			reloadWindow();
		}
	};
	if (browser) {
		checkRememberMe();
	}

	const login = async (): Promise<void> => {
		if (emailEmpty || passwordEmpty) {
			return;
		}
		const formData = new FormData();
		formData.append('username', loginData.email);
		formData.append('password', loginData.password);
		const res = await fetch('/api/v1/users/token/cookie', {
			method: 'post',
			body: formData
		});
		isSubmitting = true;
		if (res.status === 200) {
			responseData.data = loginData.password === '' ? 'magic' : 'password';
		} else if (res.status === 401) {
			responseData.data = '404';
		} else {
			responseData.data = 'error';
		}
		responseData.open = true;
		isSubmitting = false;
	};
</script>

<svelte:head>
	<title>ClassQuiz - Login</title>
</svelte:head>
<div class="flex items-center justify-center h-full px-4">
	<div>
		{#if verified}
			<div
				class="flex items-center justify-center p-4 text-green-700 border-2 border-current rounded-lg bg-white"
				role="alert"
			>
				<svg
					width="24"
					height="24"
					viewBox="0 0 24 24"
					class="w-6 h-6"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M10.2426 16.3137L6 12.071L7.41421 10.6568L10.2426 13.4853L15.8995 7.8284L17.3137 9.24262L10.2426 16.3137Z"
						fill="currentColor"
					/>
					<path
						fill-rule="evenodd"
						clip-rule="evenodd"
						d="M1 12C1 5.92487 5.92487 1 12 1C18.0751 1 23 5.92487 23 12C23 18.0751 18.0751 23 12 23C5.92487 23 1 18.0751 1 12ZM12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21Z"
						fill="currentColor"
					/>
				</svg>

				<h3 class="ml-3 text-sm font-medium">
					You've successfully confirmed your email address.
				</h3>
			</div>
		{/if}
		<span class="p-4" />

		<div
			class="w-full max-w-sm mx-auto overflow-hidden bg-white rounded-lg shadow-md dark:bg-gray-800"
		>
			<div class="px-6 py-4">
				<h2 class="text-3xl font-bold text-center text-gray-700 dark:text-white">
					ClassQuiz
				</h2>

				<h3 class="mt-1 text-xl font-medium text-center text-gray-600 dark:text-gray-200">
					{$t('login_page.welcome_back')}
				</h3>

				<p class="mt-1 text-center text-gray-500 dark:text-gray-400">
					{$t('login_page.login_or_create_account')}
				</p>

				<form on:submit|preventDefault={login}>
					<div class="w-full mt-4">
						<div class="dark:bg-gray-800 bg-white p-4 rounded-lg">
							<div class="relative bg-inherit w-full">
								<input
									id="email"
									bind:value={loginData.email}
									name="email"
									type="email"
									class="w-full peer bg-transparent h-10 rounded-lg text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600"
									placeholder={$t('words.email')}
								/>
								<label
									for="email"
									class="absolute cursor-text left-0 -top-3 text-sm text-gray-700 dark:text-white bg-inherit mx-1 px-1 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:top-2 peer-focus:-top-3 peer-focus:text-sky-600 peer-focus:text-sm transition-all"
								>
									{$t('words.email')}
								</label>
							</div>
						</div>
						<div class="dark:bg-gray-800 bg-white p-4 rounded-lg">
							<div class="relative bg-inherit w-full">
								<input
									id="password"
									name="password"
									type="password"
									bind:value={loginData.password}
									class="w-full peer bg-transparent h-10 rounded-lg text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600"
									placeholder={$t('words.password')}
								/>
								<label
									for="password"
									class="absolute cursor-text left-0 -top-3 text-sm text-gray-500 bg-inherit mx-1 px-1 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:top-2 peer-focus:-top-3 peer-focus:text-sky-600 peer-focus:text-sm transition-all"
								>
									{$t('words.password')}
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
								disabled={!inputValid}
								type="submit"
							>
								{#if isSubmitting}
									<svg
										class="h-4 w-4 animate-spin mx-auto my-20"
										viewBox="3 3 18 18"
									>
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
									{$t('words.login')}
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

			<div
				class="flex items-center justify-center py-4 text-center bg-gray-50 dark:bg-gray-700"
			>
				<span class="text-sm text-gray-600 dark:text-gray-200"
					>{$t('login_page.already_have_account')}
				</span>

				<a
					href="/account/register"
					class="mx-2 text-sm font-bold text-blue-500 dark:text-blue-400 hover:underline"
					>{$t('words.register')}</a
				>
			</div>
		</div>
	</div>
</div>
<Footer />
<div
	class="fixed z-10 inset-0 overflow-y-auto"
	aria-labelledby="modal-title"
	role="dialog"
	aria-modal="true"
	class:hidden={!responseData.open}
>
	<div
		class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"
	>
		<!--
        Background overlay, show/hide based on modal state.

        Entering: "ease-out duration-300"
          From: "opacity-0"
          To: "opacity-100"
        Leaving: "ease-in duration-200"
          From: "opacity-100"
          To: "opacity-0"
      -->
		<div
			class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
			aria-hidden="true"
		/>

		<!-- This element is to trick the browser into centering the modal contents. -->
		<span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true"
			>&#8203;</span
		>

		<!--
        Modal panel, show/hide based on modal state.

        Entering: "ease-out duration-300"
          From: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          To: "opacity-100 translate-y-0 sm:scale-100"
        Leaving: "ease-in duration-200"
          From: "opacity-100 translate-y-0 sm:scale-100"
          To: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
      -->
		<div
			class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"
		>
			<div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
				<div class="sm:flex sm:items-start">
					<div
						class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"
					>
						<!-- Heroicon name: outline/exclamation -->
						{#if responseData.data === '404' || responseData.data === 'error'}
							<svg
								class="h-6 w-6 text-red-600"
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
								aria-hidden="true"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
								/>
							</svg>
						{:else}
							<svg
								class="w-6 h-6 text-green-600"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
							</svg>
						{/if}
					</div>
					<div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
						<h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
							{#if responseData.data === 'magic'}
								{$t('login_page.modal.success.success_check_mail')}
							{:else if responseData.data === 'password'}
								{$t('login_page.modal.success.success')}
							{:else if responseData.data === '404'}
								{$t('login_page.modal.error.wrong_creds')}
							{:else if responseData.data === 'error'}
								{$t('login_page.modal.error.unexpected')}
							{:else}
								You stupid Mawoka!
							{/if}
						</h3>
						<div class="mt-2">
							<p class="text-sm text-gray-500">
								{#if responseData.data === 'magic'}
									{$t('login_page.modal.success.description.success_check_mail')}
								{:else if responseData.data === 'password'}
									{$t('login_page.modal.success.description.success')}
								{:else if responseData.data === '404'}
									{$t('login_page.modal.error.description.wrong_creds')}
								{:else if responseData.data === 'error'}
									{$t('login_page.modal.error.description.unexpected')}
								{:else}
									You stupid Mawoka!
								{/if}
							</p>
						</div>
					</div>
				</div>
			</div>
			<div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
				<button
					type="button"
					on:click={() => {
						responseData.open = false;
						if (responseData.data === 'magic' || responseData.data === 'password') {
							reloadWindow();
						}
					}}
					class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
					>{$t('words.close')}
				</button>
			</div>
		</div>
	</div>
</div>
