<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	// import AudioPlayer from '$lib/play/audio_player.svelte';
	import ControllerCodeDisplay from '$lib/components/controller/code.svelte';
	import { getLocalization } from '$lib/i18n';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import { fade } from 'svelte/transition';
	import { SocketGameControls } from '$lib/play/admin/socket_game_controls.ts';
	import type { GameState } from '$lib/play/admin/game_state';

	interface Props {
		game_pin: string;
		game_state: GameState;
		socket_game_controls: SocketGameControls;
		cqc_code: string;
	}

	let {
		game_pin,
		game_state = $bindable(),
		socket_game_controls,
		cqc_code = $bindable()
	}: Props = $props();

	let fullscreen_open = $state(false);
	const { t } = getLocalization();
	let play_music = $state(false);

	if (cqc_code === 'null') {
		cqc_code = null;
	}
</script>

<div class="w-full h-full">
	<!-- <AudioPlayer bind:play={play_music} /> -->
	<div class="grid grid-cols-3 pt-12">
		<!--mt-12 -->
		<div class="flex justify-center">
			<p class="m-auto text-2xl">
				{$t('play_page.join_description', {
					url:
						window.location.host === 'classquiz.de'
							? 'cquiz.de'
							: `${window.location.host}/play`,
					pin: game_pin
				})}
			</p>
		</div>
		<img
			onclick={() => (fullscreen_open = true)}
			alt="QR code to join the game"
			src="/api/v1/utils/qr/{game_pin}"
			class="block mx-auto w-1/2 dark:bg-white shadow-2xl rounded-sm hover:cursor-pointer"
		/>
		{#if cqc_code}
			<div class="m-auto">
				<div class="flex justify-center my-4">
					<p class="m-auto text-2xl">
						{#if game_state.players.length <= 1}
							{$t('play_page.players_waiting', {
								count: game_state.players.length ?? 0
							})}
						{:else}
							{$t('play_page.players_waiting_plural', {
								count: game_state.players.length ?? 0
							})}
						{/if}
					</p>
				</div>
				<div class="flex-col flex justify-center">
					<p class="mx-auto">{$t('play_page.join_by_entering_code')}</p>
					<ControllerCodeDisplay code={cqc_code} />
				</div>
			</div>
		{:else}
			<div class="flex justify-center">
				<p class="m-auto text-2xl">
					{#if game_state.players.length <= 1}
						{$t('play_page.players_waiting', {
							count: game_state.players.length ?? 0
						})}
					{:else}
						{$t('play_page.players_waiting_plural', {
							count: game_state.players.length ?? 0
						})}
					{/if}
				</p>
			</div>
		{/if}
	</div>
	<p class="text-3xl text-center">
		{$t('words.pin')}: <span class="select-all">{game_pin}</span>
	</p>
	<div class="flex justify-center w-full mt-4">
		<div>
			<GrayButton
				disabled={game_state.players.length < 1}
				onclick={() => {
					socket_game_controls.start_game();
				}}
				>{$t('admin_page.start_game')}
			</GrayButton>
		</div>
	</div>
	<div class="flex flex-row w-full mt-4 px-10 flex-wrap">
		{#if game_state.players.length > 0}
			{#each game_state.players as player}
				<div class="p-2 m-2 border-2 border-[#B07156] rounded-sm hover:cursor-pointer">
					<span
						class="hover:line-through text-lg"
						onclick={() => {
							socket_game_controls.kick_player(player.username, game_state.players);
						}}>{player.username}</span
					>
					<!--					<button>{$t('words.kick')}</button>-->
				</div>
			{/each}
		{/if}
	</div>
</div>

{#if fullscreen_open}
	<div
		class="fixed top-0 left-0 z-50 w-screen h-screen bg-black/50 flex p-2"
		transition:fade|global={{ duration: 80 }}
		onclick={() => (fullscreen_open = false)}
		tabindex="0"
		role="button"
		aria-label="Close modal"
		onkeydown={(e) =>
			e.key === 'Enter' || e.key === ' '
				? () => {
						fullscreen_open = false;
					}
				: null}
	>
		<img
			alt="QR code to join the game"
			src="/api/v1/utils/qr/{game_pin}"
			class="object-contain rounded-sm m-auto h-full bg-white"
		/>
	</div>
{/if}
