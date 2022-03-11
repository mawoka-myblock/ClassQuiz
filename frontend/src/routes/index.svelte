<script lang="ts">
	import { navbarVisible } from '$lib/stores';
	navbarVisible.set(true);
</script>

<svelte:head>
	<title>ClassQuiz - Home</title>
	<meta name="description" content="ClassQuiz is a quiz app like KAHOOT! for students, which is open source and free to use.">
</svelte:head>

<section>
	<div class="pt-12 text-center">
		<h1 class="sm:text-8xl text-6xl mt-6 marck-script">ClassQuiz</h1>
		<p class="text-xl mt-4">The open-source quiz-platform!</p>
	</div>
</section>
<section id="features">
	<div class="text-center pt-48 snap-y">
		<h1 class="sm:text-6xl text-4xl">Features</h1>
		<p class="text-xl pt-4">
			ClassQuiz is a quiz-platform that allows you to create and manage quizzes.
			<br />
			The main feature is a KAHOOT!-import function that allows you to import quizzes from KAHOOT!-quizzes.
		</p>
	</div>
</section>
