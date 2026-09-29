<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	// Was a hand-rolled overlay: `w-1/3` (about 130px wide on a phone), `bg-white`, a
	// window keydown listener that was never removed, and two formats. It is Excel only
	// now (MVP.md D5): the other format, .cqa, exists to be re-imported, and Import is
	// hidden for the MVP (D6). To bring .cqa back, add a second link to
	// /api/v1/eximport/{quiz_id} with $t('downloader.own_format').
	import { getLocalization } from '$lib/i18n';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Button } from '$lib/components/ui/button';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';

	const { t } = getLocalization();

	interface Props {
		quiz_id?: string | null;
	}

	let { quiz_id = $bindable(null) }: Props = $props();

	const open = $derived(quiz_id !== null);
	const on_open_change = (is_open: boolean) => {
		if (!is_open) quiz_id = null;
	};
</script>

<Dialog.Root {open} onOpenChange={on_open_change}>
	<Dialog.Content class="gap-5 sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title>{$t('downloader.title')}</Dialog.Title>
			<Dialog.Description>{$t('downloader.excel_help')}</Dialog.Description>
		</Dialog.Header>
		<Dialog.Footer>
			<Button variant="outline" onclick={() => (quiz_id = null)}>
				{$t('words.cancel')}
			</Button>
			<!-- A plain link: the export is an attachment, so following it downloads without
			     leaving the page. The close waits a task: closing inside the handler would
			     re-render this href as ".../null" before the browser follows it. -->
			<Button
				href="/api/v1/eximport/excel/{quiz_id}"
				onclick={() => setTimeout(() => (quiz_id = null))}
			>
				<FileSpreadsheet />
				{$t('downloader.excel_button')}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
