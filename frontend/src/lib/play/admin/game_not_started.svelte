<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import AudioPlayer from '$lib/play/audio_player.svelte';
	import ControllerCodeDisplay from '$lib/components/controller/code.svelte';
	import { getLocalization } from '$lib/i18n';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import { fade } from 'svelte/transition';

	export let game_pin: string;
	export let players;
	export let socket;
	export let cqc_code: string;

	let fullscreen_open = false;
	const { t } = getLocalization();
	let play_music = false;

	if (cqc_code === 'null') {
		cqc_code = null;
	}

	const kick_player = (username: string) => {
		socket.emit('kick_player', { username: username });
		for (let i = 0; i < players.length; i++) {
			console.log(players[i].username, username);
			if (players[i].username === username) {
				players.splice(i, 1);
				break;
			}
		}
		players = players;
	};
</script>

<div class="w-full h-full">
	<AudioPlayer bind:play={play_music} />
	<div class="grid grid-cols-3 mt-12">
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
			on:click={() => (fullscreen_open = true)}
			alt="QR code to join the game"
			src="/api/v1/utils/qr/{game_pin}"
			class="block mx-auto w-1/2 dark:bg-white shadow-2xl rounded hover:cursor-pointer"
		/>
		{#if cqc_code}
			<div class="m-auto">
				<div class="flex justify-center my-4">
					<p class="m-auto text-2xl">
						{$t('play_page.players_waiting', {
							count: players.length ?? 0
						})}
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
					{$t('play_page.players_waiting', {
						count: players.length ?? 0
					})}
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
				disabled={players.length < 1}
				on:click={() => {
					socket.emit('start_game', '');
				}}
				>{$t('admin_page.start_game')}
			</GrayButton>
		</div>
	</div>
	<div class="flex flex-row w-full mt-4 px-10 flex-wrap">
		{#if players.length > 0}
			{#each players as player}
				<div class="p-2 m-2 border-2 border-[#B07156] rounded hover:cursor-pointer">
					<span
						class="hover:line-through text-lg"
						on:click={() => {
							kick_player(player.username);
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
		class="fixed top-0 left-0 z-50 w-screen h-screen bg-black bg-opacity-50 fle p-2"
		transition:fade={{ duration: 80 }}
		on:click={() => (fullscreen_open = false)}
	>
		<img
			alt="QR code to join the game"
			src="/api/v1/utils/qr/{game_pin}"
			class="object-contain rounded m-auto h-full bg-white"
		/>
	</div>
{/if}
