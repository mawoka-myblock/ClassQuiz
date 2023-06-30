<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import { SaveStatus } from './commons';
	import SaveIndicator from './SaveIndicator.svelte';
	import Spinner from '$lib/Spinner.svelte';
	import Cookies from 'js-cookie';
	import { browser } from '$app/environment';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	export let data: PageData;
	const controller = data.controller;

	let newest_version: string | undefined = undefined;

	let saved_status = SaveStatus.Unchanged;

	let save_player_timer;
	const save_player_name_debounce = () => {
		clearTimeout(save_player_timer);
		save_player_timer = setTimeout(save_names, 750);
	};

	const save_names = async () => {
		if (!browser) {
			return;
		}
		saved_status = SaveStatus.Saving;
		const res = await fetch(`/api/v1/box-controller/web/modify`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				id: controller.id,
				player_name: controller.player_name,
				name: controller.name
			})
		});
		if (res.ok) {
			saved_status = SaveStatus.Saved;
		} else {
			saved_status = SaveStatus.Error;
		}
	};
	const get_latest_version = async () => {
		if (!browser) {
			return;
		}
		const cookie_data = Cookies.get('latest_cqc_version');
		if (cookie_data) {
			newest_version = cookie_data;
			return;
		}
		const res = await fetch(
			'https://api.github.com/repos/mawoka-myblock/ClassQuizController/releases'
		);
		const json = await res.json();
		newest_version = json[0].tag_name.replace('v', '');
		Cookies.set('latest_cqc_version', newest_version, { path: '', expires: 3600 });
	};

	const allow_update_to_version = async () => {
		if (newest_version === controller.os_version) {
			return;
		}
		let wanted_version;
		if (newest_version === controller.wanted_os_version) {
			wanted_version = controller.os_version;
		} else {
			wanted_version = newest_version;
		}
		await fetch('/api/v1/box-controller/web/set_update', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ id: controller.id, version: wanted_version })
		});
		window.location.reload();
	};
</script>

<div>
	<div class="w-full flex flex-col">
		<h2 class="text-2xl mx-auto">{$t('controllers.controller_name')}</h2>
		<div class="mx-auto flex">
			<input
				class="rounded p-1 transition-all outline-none text-center dark:bg-gray-700"
				bind:value={controller.name}
				on:keyup={save_player_name_debounce}
			/>
			<SaveIndicator status={saved_status} />
		</div>
	</div>
	<div class="flex flex-col">
		<h2 class="mx-auto text-2xl">{$t('controllers.player_name')}</h2>
		<div class="mx-auto flex">
			<input
				class="rounded p-1 transition-all outline-none text-center dark:bg-gray-700"
				bind:value={controller.player_name}
				on:keyup={save_player_name_debounce}
			/>
			<SaveIndicator status={saved_status} />
		</div>
	</div>
	<div class="flex flex-col">
		<h2 class="mx-auto text-2xl">{$t('words.update')}</h2>
		{#await get_latest_version()}
			<Spinner my_20={false} />
		{:then _}
			<p class="mx-auto">
				{$t('controllers.version_overview', {
					newest_version,
					current_version: controller.os_version
				})}
			</p>
		{/await}
		{#if newest_version && controller.os_version}
			<div class="mx-auto">
				<BrownButton
					disabled={newest_version === controller.os_version}
					on:click={allow_update_to_version}
				>
					{#if newest_version === controller.os_version}
						{$t('controllers.already_latest_version')}
					{:else if newest_version === controller.wanted_os_version}
						{$t('controllers.cancel_update')}
					{:else}
						{$t('controllers.update_from_to', {
							newest_version,
							current_version: controller.os_version
						})}
					{/if}
				</BrownButton>
			</div>
		{/if}
	</div>
</div>
