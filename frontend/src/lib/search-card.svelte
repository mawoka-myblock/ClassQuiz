<script>
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	export let quiz;
	export let enable_html = false;
	import ImportedOrNot from '$lib/view_quiz/imported_or_not.svelte';
</script>

<div class="flex justify-center">
	<a href="/view/{quiz.id}" class="h-max w-fit">
		<div class="max-w-md py-4 px-8 bg-white shadow-lg rounded-lg my-20 dark:bg-slate-800">
			<!--			<div class='flex justify-center md:justify-end -mt-16'>
							<img class='w-20 h-20 object-cover rounded-full border-2 border-indigo-500'
								 src='https://images.unsplash.com/photo-1499714608240-22fc6ad53fb2?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80'>
						</div>-->
			<div>
				<div class="flex w-full items-center">
					<h2
						class="text-gray-800 dark:text-gray-200 text-3xl font-semibold truncate pr-2"
					>
						{#if enable_html}
							{@html quiz.title}
						{:else}
							{quiz.title}
						{/if}
					</h2>
					<span class="inline-block ml-auto">
						<ImportedOrNot imported={quiz.imported_from_kahoot} />
					</span>
				</div>
				<p
					class="mt-2 text-gray-600 dark:text-gray-300 break-all overflow-hidden text-ellipsis max-h-[4.5rem] block"
				>
					{#if enable_html} {@html quiz.description}{:else}{quiz.description} {/if}
				</p>
			</div>
			<div class="flex mt-4">
				<span
					>{$t('explore_page.made_by')}
					{#if enable_html}{@html quiz.user}{:else}{quiz.user}{/if}</span
				>
			</div>
		</div>
	</a>
</div>
