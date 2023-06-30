<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	// import { alertModal } from '$lib/stores';

	export let session_data;
	export let selected_method;
	export let done;
	export let step;

	const { t } = getLocalization();
	let isSubmitting;
	let totp = '';

	let totp_valid = false;

	$: totp_valid = totp.length === 6;

	const continue_in_login = async () => {
		if (!totp_valid) {
			return;
		}
		const res = await fetch(
			`/api/v1/login/step/${step}?session_id=${session_data.session_id}`,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ auth_type: 'TOTP', data: totp })
			}
		);
		if (res.status === 200) {
			done = true;
		} else if (res.status === 202) {
			step += 1;
			selected_method = null;
		} else if (res.status === 401) {
			let data;
			try {
				data = await res.json();
			} catch {
				/*				alertModal.set({
					open: true,
					body: "This shouldn't happen. Please try again.",
					title: 'Unknown error'
				});*/
				alert('Unknown error');
				window.location.reload();
			}
			if (data.detail === 'totp wrong') {
				/*				alertModal.set({
					open: true,
					body: 'Wrong Totp-Code. please try again.',
					title: 'Totp Error'
				});*/
				alert('TOTP code was incorrect');
				totp = '';
			}
		}
	};
</script>

<div class="px-6 py-4">
	<h2 class="text-3xl font-bold text-center text-gray-700 dark:text-white">ClassQuiz</h2>

	<form on:submit|preventDefault={continue_in_login}>
		<div class="w-full mt-4">
			<div class="dark:bg-gray-800 bg-white p-4 rounded-lg">
				<div class="relative bg-inherit w-full">
					<input
						id="totp"
						bind:value={totp}
						name="totp"
						type="text"
						class="w-full peer bg-transparent h-10 rounded-lg text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600"
						placeholder={$t('words.totp')}
						autocomplete="one-time-code"
					/>
					<label
						for="totp"
						class="absolute cursor-text left-0 -top-3 text-sm text-gray-700 dark:text-white bg-inherit mx-1 px-1 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:top-2 peer-focus:-top-3 peer-focus:text-sky-600 peer-focus:text-sm transition-all"
					>
						{$t('words.totp')}
					</label>
				</div>
			</div>
			<div class="flex items-center justify-between mt-4">
				<button
					on:click={() => {
						selected_method = 'BACKUP';
					}}
					class="text-sm text-gray-600 dark:text-gray-200 hover:text-gray-500"
					>{$t('login_page.use_backup_code')}</button
				>
				<button
					class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
					disabled={!totp_valid}
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
		</div>
	</form>
</div>
