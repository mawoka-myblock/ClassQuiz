<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<svelte:head>
	<title>ClassQuiz/docs - Import from Kahoot</title>
	<meta
		name="description"
		content="How to import quizzes from KAHOOT! into ClassQuiz, the open-source quiz-application,  easily"
	/>
</svelte:head>
<article
	class="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto mt-10 prose-slate px-4 dark:prose-invert"
>
	<h1>Import Quizzes from Kahoot into ClassQuiz</h1>

	<p>
		All in all, this procedure is pretty simple, so just go to <a
			href="https://create.kahoot.it/discover"
			rel="nofollow"
			target="_blank">create.kahoot.it/discover</a
		>, find the quiz you want to import, click on it and copy the URL into your clipboard. Then
		go to
		<a href="https://classquiz.de/import" rel="nofollow" target="_blank">classquiz.de/import</a>
		and paste the url into the text field.
	</p>

	<h2>Limitations</h2>
	<ul>
		<li>Videos don't get imported</li>
		<li>Metadata doesn't get imported (Stuff like create-date, cover-image, etc.)</li>
		<li>Point-multipliers don't get imported</li>
	</ul>
</article>
