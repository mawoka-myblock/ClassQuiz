<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { createForm } from 'felte';
	import { getLocalization } from '$lib/i18n';
	import { validateSchema } from '@felte/validator-yup';
	import { navbarVisible } from '$lib/stores';
	import Footer from '$lib/footer.svelte';

	const { t } = getLocalization();
	import reporter from '@felte/reporter-tippy';

	navbarVisible.set(true);
	import * as yup from 'yup';

	const registerSchema = yup.object({
		email: yup.string().email('Email must be valid!').required(),
		password1: yup
			.string()
			.required()
			.min(8, 'Password must be at least 8 characters long!')
			.max(100, 'Password must be at most 100 characters long!'),
		password2: yup
			.string()
			.required()
			.test('equal', 'Passwords do not match!', function (v) {
				const ref = yup.ref('password1');
				return v === this.resolve(ref);
			}),
		username: yup
			.string()
			.required()
			.min(3, 'Username must be at least 3 characters long')
			.max(20, 'Username must be at most 20 characters long'),
		privacy_accept: yup
			.boolean()
			.oneOf([true], 'You must accept the privacy policy to register!'),
		tos_accept: yup.boolean().oneOf([true], 'You must accept the terms of service to register!')
	});

	const { form, errors, touched, isValid, isSubmitting } = createForm<
		yup.InferType<typeof registerSchema>
	>({
		validate: validateSchema(registerSchema),
		extend: [reporter()],
		onSubmit: async (values) => {
			const res = await fetch('/api/v1/users/create', {
				method: 'post',
				body: JSON.stringify({
					email: values.email,
					password: values.password1,
					username: values.username
				}),
				headers: {
					'Content-Type': 'application/json'
				}
			});
			if (res.status === 200) {
				responseData.data = '200';
			} else if (res.status === 409) {
				responseData.data = '409';
			} else if (res.status === 400) {
				responseData.data = '400';
			} else {
				responseData.data = 'error';
			}
			responseData.open = true;
		}
	});
	let responseData = {
		open: false,
		data: ''
	};
</script>

<svelte:head>
	<title>ClassQuiz - Register</title>
</svelte:head>
<div class="flex items-center justify-center h-full px-4">
	<div>
		<div
			class="w-full max-w-sm mx-auto overflow-hidden bg-white rounded-lg shadow-md dark:bg-gray-800"
		>
			<div class="px-6 py-4">
				<h2 class="text-3xl font-bold text-center text-gray-700 dark:text-white">
					ClassQuiz
				</h2>

				<h3 class="mt-1 text-xl font-medium text-center text-gray-600 dark:text-gray-200">
					{$t('register_page.greeting')}
				</h3>

				<p class="mt-1 text-center text-gray-500 dark:text-gray-400">
					{$t('register_page.create_account')}
				</p>

				<form use:form>
					<div class="w-full mt-4">
						<div class="dark:bg-gray-800 bg-white p-4 rounded-lg">
							<div class="relative bg-inherit w-full">
								<input
									id="email"
									name="email"
									type="email"
									class="w-full peer bg-transparent h-10 rounded-lg text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600"
									placeholder={$t('words.email')}
									class:ring-red-700={$errors.email !== null}
									class:ring-green-600={$touched.email === true &&
										$errors.email === null}
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
									id="username"
									name="username"
									type="text"
									class="w-full peer bg-transparent h-10 rounded-lg text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600"
									placeholder={$t('words.username')}
									class:ring-red-700={$errors.username !== null}
									class:ring-green-600={$touched.username === true &&
										$errors.username === null}
								/>
								<label
									for="username"
									class="absolute cursor-text left-0 -top-3 text-sm text-gray-700 dark:text-white bg-inherit mx-1 px-1 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:top-2 peer-focus:-top-3 peer-focus:text-sky-600 peer-focus:text-sm transition-all"
								>
									{$t('words.username')}
								</label>
							</div>
						</div>
						<div class="dark:bg-gray-800 bg-white p-4 rounded-lg">
							<div class="relative bg-inherit w-full">
								<input
									id="password1"
									name="password1"
									type="password"
									class:ring-red-700={$errors.password1 !== null}
									class:ring-green-600={$touched.password1 === true &&
										$errors.password1 === null}
									class="w-full peer bg-transparent h-10 rounded-lg text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600"
									placeholder={$t('words.password')}
								/>
								<label
									for="password1"
									class="absolute cursor-text left-0 -top-3 text-sm text-gray-500 bg-inherit mx-1 px-1 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:top-2 peer-focus:-top-3 peer-focus:text-sky-600 peer-focus:text-sm transition-all"
								>
									{$t('words.password')}
								</label>
							</div>
						</div>
						<div class="dark:bg-gray-800 bg-white p-4 rounded-lg">
							<div class="relative bg-inherit w-full">
								<input
									id="password2"
									name="password2"
									type="password"
									class="w-full peer bg-transparent h-10 rounded-lg text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600"
									placeholder={$t('words.password')}
									class:ring-red-700={$errors.password2 !== null}
									class:ring-green-600={$touched.password2 === true &&
										$errors.password2 === null}
								/>
								<label
									for="password2"
									class="absolute cursor-text left-0 -top-3 text-sm text-gray-500 bg-inherit mx-1 px-1 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:top-2 peer-focus:-top-3 peer-focus:text-sky-600 peer-focus:text-sm transition-all"
								>
									{$t('words.password')}
								</label>
							</div>
						</div>
						<div
							class="ring-1 ring-gray-500 focus:outline-none rounded-lg m-4 py-2"
							class:ring-red-700={$errors.privacy_accept !== null}
							class:ring-green-600={$touched.privacy_accept === true &&
								$errors.privacy_accept === null}
						>
							<!--						<div class='flex items-center justify-between mt-4 w-full'>-->
							<input type="checkbox" name="privacy_accept" class="ml-3" />
							<label class="text-sm text-gray-600 dark:text-gray-200">
								I've read the <a href="/docs/privacy-policy" class="underline"
									>Privacy policy</a
								>.
							</label>
						</div>
						<div
							class="ring-1 ring-gray-500 focus:outline-none rounded-lg m-4 py-2"
							class:ring-red-700={$errors.tos_accept !== null}
							class:ring-green-600={$touched.tos_accept === true &&
								$errors.tos_accept === null}
						>
							<!--						<div class='flex items-center justify-between mt-4 w-full'>-->
							<input type="checkbox" name="tos_accept" class="ml-3" />
							<label class="text-sm text-gray-600 dark:text-gray-200">
								I agree to the <a href="/docs/tos" class="underline"
									>Terms of Service</a
								>.
							</label>
						</div>

						<div class="flex items-center justify-between mt-4">
							<a
								href="/account/reset-password"
								class="text-sm text-gray-600 dark:text-gray-200 hover:text-gray-500"
								>{$t('register_page.forgot_password?')}</a
							>

							<button
								class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded hover:bg-gray-600 focus:outline-none"
								disabled={!$isValid || $isSubmitting}
								class:cursor-not-allowed={!$isValid || $isSubmitting}
								class:opacity-50={!$isValid || $isSubmitting}
								type="submit"
							>
								{#if $isSubmitting}
									<svg class="h-4 w-4 animate-spin" viewBox="3 3 18 18">
										<path
											class="fill-blue-800"
											d="M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z"
										/>
										<path
											class="fill-blue-100"
											d="M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z"
										/>
									</svg>
								{:else}
									{$t('words.register')}
								{/if}
							</button>
						</div>
					</div>
				</form>
			</div>

			<div
				class="flex items-center justify-center py-4 text-center bg-gray-50 dark:bg-gray-700"
			>
				<span class="text-sm text-gray-600 dark:text-gray-200"
					>{$t('register_page.already_have_account?')}
				</span>

				<a
					href="/account/login"
					class="mx-2 text-sm font-bold text-blue-500 dark:text-blue-400 hover:underline"
					>{$t('words.login')}</a
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
		<div
			class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
			aria-hidden="true"
		/>

		<!-- This element is to trick the browser into centering the modal contents. -->
		<span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true"
			>&#8203;</span
		>
		<div
			class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"
		>
			<div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
				<div class="sm:flex sm:items-start">
					<div
						class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"
					>
						<!-- Heroicon name: outline/exclamation -->
						{#if responseData.data === '409' || responseData.data === 'error' || responseData.data === '400'}
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
							{#if responseData.data === '409'}
								Account already exists!
							{:else if responseData.data === 'error'}
								Unexpected error!
							{:else if responseData.data === '200'}
								Sign up successfully!
							{:else if responseData.data === '400'}
								Wrong email!
							{:else}
								You stupid Mawoka!
							{/if}
						</h3>
						<div class="mt-2">
							<p class="text-sm text-gray-500">
								{#if responseData.data === '200'}
									<!-- TODO: Add translation -->
									You signed up successfully! Please check your mailbox to confirm
									your email address!
								{:else if responseData.data === '409'}
									An account with that email-address already exists!
								{:else if responseData.data === '400'}
									This email-address doesn't exist!
								{:else if responseData.data === 'error'}
									There was the good old unexpected error!
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
						window.location.assign('/');
					}}
					class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
					>{$t('words.close')}
				</button>
			</div>
		</div>
	</div>
</div>
