<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->
<script lang="ts">
	export let session_data = {};
	export let step;
	export let selected_method;

	let available_methods;

	const set_available_methods = (step_var: number) => {
		if (step_var === 1) {
			available_methods = session_data.step_1;
		} else if (step_var === 2) {
			available_methods = session_data.step_2;
		}
	};

	$: set_available_methods(step);
</script>

<div class="px-6 py-4">
	<h2 class="text-3xl font-bold text-center text-gray-700 dark:text-white">ClassQuiz</h2>

	<div class="w-full mt-4">
		<div class="dark:bg-gray-800 bg-white p-4 rounded-lg">
			<ul class="flex flex-col gap-4">
				{#if available_methods.includes('PASSKEY')}
					<div
						class="flex flex-row bg-gray-100 dark:bg-gray-700 rounded-lg p-2 hover:cursor-pointer hover:bg-gray-200 transition"
						on:click={() => {
							selected_method = 'PASSKEY';
						}}
						on:keyup={() => {
							selected_method = 'PASSKEY';
						}}
					>
						<!-- heroicons/key -->
						<svg
							class="w-12 h-12"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
							/>
						</svg>
						<div class="ml-2">
							<p>Key</p>
							<p class="text-sm">Authenticate using a security key</p>
						</div>
					</div>
				{/if}
				{#if available_methods.includes('PASSWORD')}
					<div
						class="flex flex-row bg-gray-100 dark:bg-gray-700 rounded-lg p-2 hover:cursor-pointer hover:bg-gray-200 transition"
						on:click={() => {
							selected_method = 'PASSWORD';
						}}
						on:keyup={() => {
							selected_method = 'PASSWORD';
						}}
					>
						<!-- iconoir/password-cursor -->
						<svg
							class="w-12 h-12 dark:text-white"
							stroke-width="2"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								d="M21 13V8a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h7"
								stroke="currentColor"
								stroke-width="2.03"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
							<path
								clip-rule="evenodd"
								d="M20.879 16.917c.494.304.463 1.043-.045 1.101l-2.567.291-1.151 2.312c-.228.459-.933.234-1.05-.334l-1.255-6.116c-.099-.48.333-.782.75-.525l5.318 3.271z"
								stroke="currentColor"
								stroke-width="2.03"
							/>
							<path
								d="M12 11.01l.01-.011M16 11.01l.01-.011M8 11.01l.01-.011"
								stroke="currentColor"
								stroke-width="2.03"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
						<div class="ml-2">
							<p>Password</p>
							<p class="text-sm">Authenticate using a Password</p>
						</div>
					</div>
				{/if}
				{#if available_methods.includes('TOTP')}
					<div
						class="flex flex-row bg-gray-100 rounded-lg p-2 hover:cursor-pointer hover:bg-gray-200 transition"
						on:click={() => {
							selected_method = 'TOTP';
						}}
						on:keyup={() => {
							selected_method = 'TOTP';
						}}
					>
						<!-- heroicons/clock -->
						<svg
							class="w-12 h-12"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<div class="ml-2">
							<p>Totp</p>
							<p class="text-sm">Authenticate using a one-time password</p>
						</div>
					</div>
				{/if}
			</ul>
		</div>
	</div>
</div>
