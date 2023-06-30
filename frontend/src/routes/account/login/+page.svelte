<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { alertModal, navbarVisible } from '$lib/stores';
	import { slide } from 'svelte/transition';
	import Footer from '$lib/footer.svelte';
	import VerifiedBadge from './verified_badge.svelte';
	import StartWindow from './start_window.svelte';
	import SelectMethod from './select_method.svelte';
	import PasswordComponent from './password_component.svelte';
	import WebauthnComponent from './webauthn_component.svelte';
	import BackupComponent from './backup_component.svelte';
	import TotpComponent from './totp_component.svelte';
	import { browserSupportsWebAuthn } from '@simplewebauthn/browser';

	navbarVisible.set(true);

	export let data;
	const { verified }: boolean = data;

	let session_data = {};
	let step = 0;
	let selected_method = null;
	let done = false;

	const redirect_back = (done_var: boolean) => {
		if (done_var) {
			window.location.reload();
		}
	};
	let alertModalOpen = false;
	$: redirect_back(done);

	alertModal.subscribe((data) => {
		if (!alertModalOpen && data.open) {
			alertModalOpen = true;
		}
		if (alertModalOpen && !data.open) {
			window.location.reload();
		}
	});

	const check_auto = () => {
		if (step === 1) {
			if (!browserSupportsWebAuthn()) {
				for (let i = 0; i < session_data.step_1.length; i++) {
					if (session_data.step_1[i] === 'PASSKEY') {
						session_data.step_1.splice(i, 1);
					}
				}
				session_data.step_1 = session_data.step_1;
			}
			if (session_data.step_1.length === 1) {
				selected_method = session_data.step_1[0];
			}
		}
		if (step === 2) {
			if (!browserSupportsWebAuthn()) {
				for (let i = 0; i < session_data.step_2.length; i++) {
					if (session_data.step_2[i] === 'PASSKEY') {
						session_data.step_2.splice(i, 1);
					}
				}
				session_data.step_2 = session_data.step_2;
			}
			if (session_data.step_2.length === 1) {
				selected_method = session_data.step_2[0];
			}
		}
	};
	$: {
		check_auto();
		step;
	}
</script>

<svelte:head>
	<title>ClassQuiz - Login</title>
</svelte:head>
<div class="flex items-center justify-center h-full px-4">
	{#if verified}
		<VerifiedBadge />
	{/if}

	<div
		class="lg:w-1/3 max-w-sm mx-auto overflow-hidden bg-white rounded-lg shadow-2xl dark:bg-gray-800"
	>
		{#if step === 0}
			<!--			<p>StartWindow</p>-->
			<div transition:slide>
				<StartWindow bind:session_data bind:step />
			</div>
		{:else if selected_method === null}
			<!--			<p>SelectWindow</p>-->
			<div transition:slide>
				<SelectMethod bind:session_data bind:step bind:selected_method />
			</div>
		{:else if selected_method === 'PASSWORD'}
			<!--			<p>PasswordWindow</p>-->
			<div transition:slide>
				<PasswordComponent bind:session_data bind:done bind:step bind:selected_method />
			</div>
		{:else if selected_method === 'PASSKEY'}
			<!--			<p>WebauthnWindow</p>-->
			<div transition:slide>
				<WebauthnComponent bind:session_data bind:done bind:step bind:selected_method />
			</div>
		{:else if selected_method === 'BACKUP'}
			<!--			<p>BackupWindow</p>-->
			<div transition:slide>
				<BackupComponent bind:session_data bind:done bind:step bind:selected_method />
			</div>
		{:else if selected_method === 'TOTP'}
			<!--			<p>TotpWindow</p>-->
			<div transition:slide>
				<TotpComponent bind:session_data bind:done bind:step bind:selected_method />
			</div>
		{/if}
	</div>
</div>
<Footer />
