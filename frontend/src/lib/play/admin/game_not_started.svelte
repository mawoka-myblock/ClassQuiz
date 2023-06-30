<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import AudioPlayer from '$lib/play/audio_player.svelte';
	import ControllerCodeDisplay from '$lib/components/controller/code.svelte';
	import { getLocalization } from '$lib/i18n';

	export let game_pin: string;
	export let players;
	export let socket;

	export let cqc_code: string;
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
			alt="QR code to join the game"
			src="/api/v1/utils/qr/{game_pin}"
			class="block mx-auto w-1/2 dark:bg-white"
		/>
		{#if cqc_code}
			<div class="m-auto">
				<div class="flex-col flex justify-center">
					<p class="mx-auto">{$t('play_page.join_by_entering_code')}</p>
					<ControllerCodeDisplay code={cqc_code} />
				</div>
			</div>
		{/if}
	</div>
	<p class="text-3xl text-center">{$t('words.pin')}: {game_pin}</p>
	<div class="flex justify-center w-full mt-4">
		<ul class="list-disc pl-8">
			{#if players.length > 0}
				{#each players as player}
					<li>
						<span
							class="hover:line-through"
							on:click={() => {
								kick_player(player.username);
							}}>{player.username}</span
						>
						<!--					<button>{$t('words.kick')}</button>-->
					</li>
				{/each}
			{/if}
		</ul>
	</div>
	{#if players.length > 0}
		<div class="flex justify-center w-full mt-4">
			<button
				class="ml-4 admin-button"
				id="startGame"
				on:click={() => {
					socket.emit('start_game', '');
				}}
				>{$t('admin_page.start_game')}
			</button>
		</div>
	{/if}
</div>
