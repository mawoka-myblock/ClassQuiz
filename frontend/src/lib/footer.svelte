<!-- GitHub link hidden for the MVP (MVP.md §4.2); the repo is at
     https://github.com/ogfrench/frogQuiz if it comes back. The legal pages stay:
     registration links to two of them, and attribution is the upstream credit. -->
<footer
	class="border-border bg-muted text-muted-foreground flex w-full flex-col items-center border-t py-6 text-center text-sm"
>
	<p>Designed with ❤️ by François &amp; Gonçalo.</p>
	<nav aria-label="Legal" class="mt-1 flex flex-wrap items-center justify-center gap-x-4">
		{#each [['/docs/tos', 'Terms of Service'], ['/docs/privacy-policy', 'Privacy'], ['/docs/attribution', 'Attribution']] as [href, label] (href)}
			<a
				{href}
				class="fq-touch-target hover:text-foreground relative inline-flex min-h-11 items-center underline underline-offset-4 transition-colors"
				>{label}</a
			>
		{/each}
	</nav>
</footer>
