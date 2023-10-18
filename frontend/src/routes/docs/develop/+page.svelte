<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import '$lib/hljs.css';

	onMount(async () => {
		const { default: hljs } = await import('highlight.js/lib/common');
		hljs.highlightAll();
	});
</script>

<svelte:head>
	<title>ClassQuiz/docs - Development-setup</title>
	<meta
		name="description"
		content="How to import quizzes from KAHOOT! into ClassQuiz, the open-source quiz-application,  easily"
	/>
</svelte:head>
<article
	class="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto mt-10 prose-slate px-4 dark:prose-invert"
>
	<h1>Development-setup</h1>

	<h2>Requirements</h2>
	<ul>
		<li>
			<a href="https://www.python.org/">Python</a><br /><i
				>I just plan to support the most recent version of Python.</i
			><br /><i>At least Python 3.10</i>
		</li>
		<li><a href="https://caddyserver.com/">Caddy</a></li>
		<li><a href="https://pipenv.pypa.io/en/latest/">Pipenv</a></li>
		<li>Linux</li>
		<li><a href="https://docker.com">Docker</a></li>
		<li><a href="https://pnpm.io/">pnpm</a> (at least node 18)</li>
	</ul>

	<h2>Setup</h2>
	<ul>
		<li>
			Clone the repo:
			<pre><code>git clone https://github.com/mawoka-myblock/ClassQuiz</code></pre>
		</li>
		<li>
			Install the dependencies
			<ul>
				<li>
					Python:
					<pre><code>pipenv install -d</code></pre>
				</li>
				<li>
					JS:
					<pre><code>cd frontend && pnpm i</code></pre>
				</li>
			</ul>
		</li>
		<li>
			Start the other services
			<p>
				There's a small helper-script: It's called <code>run_tests.sh</code> and does more than
				you think.
			</p>
			<h4>run_tests.sh - Docs</h4>
			<p>
				You can run this script with bash. It helps you managing docker-containers you need
				to run ClassQuiz. The standard workflow is the following:
			</p>
			<ol>
				<li>
					Prepare all the containers:
					<pre><code>./run_tests.sh +</code></pre>
				</li>
				<li>
					Start the Python-server:
					<pre><code>pipenv run uvicorn classquiz:app --reload --proxy-headers</code
						></pre>
				</li>
				<li>
					Start the background worker:
					<pre><code>pipenv run arq classquiz.worker.WorkerSettings</code></pre>
				</li>
				<li>
					Start the frontend-dev-server:
					<pre><code>cd frontend && API_URL=http://localhost:8080 pnpm dev</code></pre>
				</li>
				<li>
					Start Caddy:
					<pre><code>caddy run</code></pre>
				</li>
				<li>
					Start the background-worker:
					<pre><code>arq classquiz.worker.WorkerSettings</code></pre>
				</li>
			</ol>
			<p>If you're done developing: <code>./run_tests.sh -</code></p>
			<p>If you want to run all the tests: <code>./run_tests.sh a</code></p>
		</li>
		<li>
			Add the following line to your <code>/etc/hosts</code>-file, so you can visit ClassQuiz
			via <code>test.com</code> (Required for the Captcha and Mapbox)
			<pre><code>127.0.0.1 test.com</code></pre>

			Now you can visit ClassQuiz at<a
				href="http://test.com:8080"
				rel="nofollow"
				target="_blank">http://test.com:8080</a
			>.
		</li>
		<li>
			Set your config up in your .env-file. What you have to set up can you see in the
			<code>classquiz/config.py</code>-file. The things you have to set are the following:
			<ul>
				<li><code>hcaptcha_key</code></li>
				<li><code>mail_address</code></li>
				<li><code>mail_password</code></li>
				<li><code>mail_username</code></li>
				<li><code>mail_server</code></li>
				<li><code>mail_port</code></li>
				<li><code>secret_key</code></li>
			</ul>
			<p>
				You'll have to set up the storage. For developing, I'd recommend using the local
				file system. to do that, set the following 2 environment-varialbes:
			</p>
			<ul>
				<li><code>STORAGE_PATH=/tmp/storage</code></li>
				<li><code>STORAGE_BACKEND=local</code></li>
			</ul>
		</li>
		<li>
			Start the server
			<ul>
				<li>
					Backend:
					<pre><code>pipenv run uvicorn classquiz:app --reload --proxy-headers</code
						></pre>
				</li>
				<li>
					Frontend:
					<pre><code>cd frontend && API_URL=http://localhost:8080 pnpm dev</code></pre>
				</li>
			</ul>
		</li>
	</ul>

	<h2>Pre-Commit</h2>
	<p>
		We're using <a href="https://pre-commit.com/">Pre-Commit</a> for our pre-commit hooks. Install
		it by running the following command:
	</p>
	<pre><code>pipenv run pre-commit install</code></pre>

	<h2>BEFORE you submit a Pull-Request</h2>
	<p>Please use <a href="https://gitmoji.dev">Gitmoji</a> for your commits.</p>
	<h4>Frontend</h4>
	<p>Please format and lint your code with</p>
	<pre><code>pnpm run format && pnpm run lint</code></pre>

	<h4>Backend</h4>
	<p>Run the tests: <code>./run_tests.sh a</code></p>
</article>
