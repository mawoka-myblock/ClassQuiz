<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<svelte:head>
	<title>ClassQuiz/docs - PoW</title>
	<meta
		name="description"
		content="Use-case of PoW for ClassQuiz, the open-source quiz-application"
	/>
</svelte:head>
<article
	class="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto mt-10 prose-slate px-4 dark:prose-invert"
>
	<h1>PoW</h1>
	<h2>Why is it loading so long?</h2>
	<p>
		Your browser is calculating something to prevent abuse. The time it takes depends on the
		power of your CPU and, believe it or not, luck. Sometimes it takes like 5 seconds, sometimes
		30 secs, so please be patient. If you want to know what's going on, go to the <a
			href="#technical">technical part</a
		>.
	</p>
	<h2 id="technical">Technical Part</h2>
	<p>
		The technique used, is called PoW, or Proof of Work. It is a way to "pay" for something by
		using your CPU. It's mainly used in crypto-stuff, but not in ClassQuiz. It's just used to
		prevent spam. Imagine it like a small fee you have to pay to upload an image, but you don't
		pay with money, instead by using your CPU intensively. The Proof of Work-algorythm used is
		called HashCash and is also used by Bitcoin. All in all, it's really simple (if you know
		what hashes are). Let me explain:
		<br />
		You're hashing a string with a counter until the first x characters (in this case 4) are "0"/zeros.
		That's it. Then, you send the counter to the server, who hashes it once, checks if the first
		x characters are really "0" and that's it.
	</p>
</article>
