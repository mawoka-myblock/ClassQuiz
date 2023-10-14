<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Smalltop from './smalltop.svelte';
	import { PopoverTypes } from '$lib/components/popover/smalltop';
	import Cookies from 'js-cookie';
	import { onMount } from 'svelte';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	let open = false;
	onMount(() => {
		if (Cookies.get('commandpalette_notice')) {
			return;
		}
		open = true;
		Cookies.set('commandpalette_notice', 'shown', {
			expires: new Date().setDate(new Date().getDate() + 30)
		});
	});
</script>

<Smalltop bind:open type={PopoverTypes.Generic} data={$t('dashboard.commandpalette_notice')} />
