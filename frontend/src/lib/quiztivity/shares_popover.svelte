<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { getLocalization } from '$lib/i18n';
	import Spinner from '$lib/Spinner.svelte';
	import { DateTime } from 'luxon';
	import { browser } from '$app/environment';
	import SmallPopover from '$lib/components/popover/smalltop.svelte';
	import { PopoverTypes } from '$lib/components/popover/smalltop';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';

	const { t } = getLocalization();
	export let open = false;
	export let id;
	let popover_open = false;
	const load_shares = async (): Promise<{
		id: string;
		name?: string;
		expire_in?: number;
		quiztivity: { id: string };
		user: { id: string };
	}> => {
		const res = await fetch(`/api/v1/quiztivity/${id}/shares`);
		return await res.json();
	};
	const copyToClipboard = (str) => {
		try {
			navigator.clipboard.writeText(str);
		} catch {
			console.log('Async Clipboard not supported');
			const el = document.createElement('textarea');
			el.value = str;
			el.setAttribute('readonly', '');
			el.style.position = 'absolute';
			el.style.left = '-9999px';
			document.body.appendChild(el);
			const selected =
				document.getSelection().rangeCount > 0
					? document.getSelection().getRangeAt(0)
					: false;
			el.select();
			document.execCommand('copy');
			document.body.removeChild(el);
			if (selected) {
				document.getSelection().removeAllRanges();
				document.getSelection().addRange(<Range>selected);
			}
		} finally {
			popover_open = true;
			setTimeout(() => {
				popover_open = false;
			}, 2000);
		}
	};

	const on_parent_click = (e: Event) => {
		if (e.target !== e.currentTarget) {
			return;
		}
		open = false;
	};
	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			open = false;
		}
	};
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});
</script>

<SmallPopover bind:open={popover_open} type={PopoverTypes.Copy} />
<div
	class="fixed w-full h-full top-0 flex bg-black bg-opacity-50 z-50"
	on:click={on_parent_click}
	transition:fade|local={{ duration: 100 }}
>
	<div
		class="m-auto bg-white dark:bg-gray-600 rounded shadow-2xl flex p-4 flex-col w-2/3 h-5/6 gap-2 overflow-scroll"
	>
		<div class="flex justify-center">
			<BrownButton>{$t('quiztivity.editor.shares.add_new_share')}</BrownButton>
		</div>
		{#await load_shares()}
			<Spinner />
		{:then shares}
			{#each shares as share}
				<div class="grid grid-cols-4 w-full gap-2">
					<!--                    <p>{share.name ?? "..."}</p>-->
					<div class="w-full mx-auto">
						<BrownButton
							flex={true}
							disabled={browser
								? !navigator.canShare({
										title: 'title',
										url: `${window.location.origin}/quiztivity`
								  })
								: false}
							on:click={() => {
								console.log(
									navigator.canShare({
										title: 'title',
										url: `${window.location.origin}/quiztivity`
									})
								);
								navigator.share({
									title: 'Quiztivity on ClassQuiz',
									text: 'Play this Quiztivity now on ClassQuiz!',
									url: `${window.location.origin}/quiztivity/share/${share.id}?ref=share`
								});
							}}
						>
							<!-- heroicons/share -->
							<svg
								aria-hidden="true"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
								class="w-5 h-5"
							>
								<path
									d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</BrownButton>
					</div>
					<div class="w-full mx-auto">
						<BrownButton
							flex={true}
							on:click={() => {
								copyToClipboard(
									`${window.location.origin}/quiztivity/share/${share.id}?ref=copy`
								);
							}}
						>
							<!-- heroicons/ClipboardCopy -->
							<svg
								aria-hidden="true"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								class="w-5 h-5"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</BrownButton>
					</div>
					<p class="m-auto">
						{#if share.expire_in}
							{$t('quiztivity.editor.shares.expires_on', {
								date: DateTime.now()
									.plus({ minutes: share.expire_in })
									.toJSDate()
									.toLocaleString()
							})}
						{:else}
							{$t('quiztivity.editor.shares.never_expires')}
						{/if}
					</p>
					<div class="w-fit my-auto ml-auto">
						<BrownButton>{$t('words.delete')}</BrownButton>
					</div>
				</div>
			{/each}
		{/await}
	</div>
</div>
