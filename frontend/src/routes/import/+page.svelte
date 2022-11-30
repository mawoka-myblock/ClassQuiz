<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible, alertModal } from '$lib/stores';

	navbarVisible.set(true);

	const { t } = getLocalization();
	let url_input = '';
	let file_input;

	let url_valid = false;
	let kahoot_regex = /^https:\/\/create\.kahoot\.it\/details\/([a-zA-Z-\d]{36})\/?$/;
	let is_loading = false;

	$: url_valid = kahoot_regex.test(url_input);

	const submit = async () => {
		if (!url_valid) {
			return;
		}
		is_loading = true;
		const regex_res = kahoot_regex.exec(url_input);
		const res = await fetch(`/api/v1/quiz/import/${regex_res[1]}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (res.status === 200) {
			window.location.href = '/dashboard';
		} else if (res.status === 400) {
			alertModal.set({
				open: true,
				title: 'Import failed',
				body: "This quiz isn't (yet) supported!"
			});
		} else {
			alertModal.set({
				open: true,
				title: 'Import failed',
				body: 'Unknown error while importing the quiz!'
			});
		}
		is_loading = false;
	};

	const file_submit = async () => {
		is_loading = true;
		const formdata = new FormData();
		formdata.append('file', file_input[0]);
		const res = await fetch('/api/v1/eximport/', {
			method: 'POST',
			body: formdata
		});
		if (res.status === 200) {
			window.location.href = '/dashboard';
		} else {
			alertModal.set({
				open: true,
				title: 'Import failed',
				body: 'Something went wrong!'
			});
		}
		is_loading = false;
	};

	$: console.log(file_input);
</script>

<svelte:head>
	<title>ClassQuiz - Import</title>
</svelte:head>

<!--{#if is_loading}
	<svg class='h-8 w-8 animate-spin mx-auto my-20' viewBox='3 3 18 18'>
		<path
			class='fill-black'
			d='M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z'
		/>
		<path
			class='fill-blue-100'
			d='M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z'
		/>
	</svg>
{:else}-->

<!--	<form on:submit|preventDefault={submit}>
		<input type='text' class="text-black w-2/5" bind:value={url_input} />
		<button type='submit' disabled={!url_valid}>Submit</button>
	</form>-->
<div class="flex items-center justify-center h-full px-4">
	<div>
		<span class="p-4" />

		<div
			class="lg:w-[64rem] lg:max-w-[64rem] w-screen max-w-screen mx-auto overflow-hidden bg-white rounded-lg shadow-md dark:bg-gray-800"
		>
			<div class="px-6 py-4">
				<h2 class="text-3xl font-bold text-center text-gray-700 dark:text-white">
					{$t('words.import')}
				</h2>

				<!--				<h3 class="mt-1 text-xl font-medium text-center text-gray-600 dark:text-gray-200">
									Welcome Back
								</h3>-->

				<!--				<p class="mt-1 text-center text-gray-500 dark:text-gray-400">
									Login or create account
								</p>-->
				<div class="grid grid-cols-2">
					<form on:submit|preventDefault={submit}>
						<div class="w-full mt-4 h-full flex flex-col">
							<h2 class="text-center text-2xl">A Kahoot!-Quiz</h2>
							<div class="dark:bg-gray-800 bg-white p-4 rounded-lg">
								<div class="relative bg-inherit w-full">
									<input
										id="url"
										bind:value={url_input}
										name="email"
										type="url"
										class="w-full peer bg-transparent h-10 rounded-lg text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600"
										placeholder="https://create.kahoot.it/details/something"
										class:ring-red-700={!url_valid}
										class:ring-green-600={url_valid}
									/>
									<label
										for="url"
										class="absolute cursor-text left-0 -top-3 text-sm text-gray-700 dark:text-white bg-inherit mx-1 px-1 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:top-2 peer-focus:-top-3 peer-focus:text-sky-600 peer-focus:text-sm transition-all"
									>
										{$t('words.url')}
									</label>
									<p class="text-sm">
										The URl should look like this:
										https://create.kahoot.it/details/...
									</p>
								</div>
								<p class="mt-2">
									On this side you can import quizzes, which live on <b>Kahoot!</b
									>.
								</p>
							</div>

							<div class="flex items-center justify-center mt-auto">
								<span />

								<button
									class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
									disabled={!url_valid || is_loading}
									type="submit"
								>
									{#if is_loading}
										<svg
											class="h-4 w-4 animate-spin mx-auto"
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
										{$t('words.submit')}
									{/if}
								</button>
							</div>
						</div>
					</form>
					<form on:submit|preventDefault={file_submit}>
						<div class="w-full mt-4 border-l-2 border-gray-600 h-full flex flex-col">
							<h2 class="text-center text-2xl">A ClassQuiz-Quiz</h2>
							<div class="dark:bg-gray-800 bg-white p-4 rounded-lg">
								<div class="relative bg-inherit w-full">
									<input
										id="file"
										bind:files={file_input}
										name="file"
										type="file"
										accept=".cqa"
										class="w-full peer bg-transparent h-10 rounded-lg py-1.5 text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600"
										class:ring-red-700={!file_input}
										class:ring-green-600={file_input}
									/>
									<p class="text-sm">Upload the file ending in .cqa</p>
								</div>
								<p class="mt-2">
									On this side you can import quizzes, which were <b
										>exported from ClassQuiz</b
									>.
								</p>
							</div>

							<div class="flex items-center justify-center mt-auto">
								<span />

								<button
									class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
									disabled={!file_input || is_loading}
									type="submit"
								>
									{#if is_loading}
										<svg
											class="h-4 w-4 animate-spin mx-auto"
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
										{$t('words.submit')}
									{/if}
								</button>
							</div>
						</div>
					</form>
				</div>
			</div>
			<div
				class="flex items-center justify-center py-4 text-center bg-gray-50 dark:bg-gray-700 mt-4"
			>
				<span class="text-sm text-gray-600 dark:text-gray-200"
					>{$t('import_page.need_help')}</span
				>

				<a
					href="/docs/import-from-kahoot"
					class="mx-2 text-sm font-bold text-blue-500 dark:text-blue-400 hover:underline"
					>{$t('import_page.visit_docs')}</a
				>
			</div>
		</div>
	</div>
</div>
<!--{/if}-->
