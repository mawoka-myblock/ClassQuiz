<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->
<script lang="ts">
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	interface Props {
		quiz_id?: string | null;
	}

	let { quiz_id = $bindable(null) }: Props = $props();

	const handle_on_click = () => {
		quiz_id = null;
	};
	onMount(() => {
		window.addEventListener('keydown', (e: KeyboardEvent) => {
			if (e.key === 'Escape') {
				quiz_id = null;
			}
		});
	});
</script>

{#if quiz_id}
	<div
		class="w-screen h-screen fixed top-0 left-0 bg-black/50 z-20 flex justify-center"
		onclick={handle_on_click}
		transition:fade={{ duration: 100 }}
	>
		<div class="m-auto w-1/3 h-auto bg-white dark:bg-gray-700 p-4 rounded-sm">
			<h1 class="text-3xl text-center mb-4">{$t('downloader.select_download_type')}</h1>
			<div class="flex flex-row gap-4">
				<div class="w-full flex justify-center">
					<BrownButton href="/api/v1/eximport/{quiz_id}"
						>{$t('downloader.own_format')}
					</BrownButton>
				</div>
				<div class="w-full flex justify-center">
					<BrownButton href="/api/v1/eximport/excel/{quiz_id}"
						>{$t('downloader.excel_format')}
					</BrownButton>
				</div>
			</div>
			<p class="mt-2 text-sm text-center">{$t('downloader.help')}</p>
		</div>
	</div>
{/if}
