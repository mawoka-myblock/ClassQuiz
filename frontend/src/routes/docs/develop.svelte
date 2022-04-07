<svelte:head>
	<title>ClassQuiz/docs - Development-setup</title>
	<meta
		name="description"
		content="How to import quizzes from KAHOOT! into ClassQuiz, the open-source quiz-application,  easily"
	/>
</svelte:head>
<article
	class="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto mt-10 prose-pink text-yellow-50 px-4"
>
	<h1>Development-setup</h1>

	<h2>Requirements</h2>
	<h4>Backend</h4>
	<ul>
		<li>
			<a href="https://www.python.org/">Python</a><br /><i
				>I just plan to support the most recent version of Python.</i
			><br /><i>At least Python 3.10</i>
		</li>
		<li><a href="https://caddyserver.com/">Caddy</a></li>
		<li><a href="https://pipenv.pypa.io/en/latest/">Pipenv</a></li>
		<li><a href="https://redis.io/">Redis</a></li>
	</ul>

	<h4>Frontend</h4>
	<ul>
		<li><a href="https://pnpm.io/">pNpM</a></li>
	</ul>

	<h2>Setup</h2>
	<ul>
		<li>
			Clone the repo:
			<pre><code>git clone https://github.com/mawoka-myblock/classquiz</code></pre>
		</li>
		<li>
			Install the dependencies
			<ul>
				<li>
					Python:
					<pre><code>pipenv install</code></pre>
				</li>
				<li>
					JS:
					<pre><code>cd frontend && pnpm i</code></pre>
				</li>
			</ul>
		</li>
		<li>
			Start the other services
			<ul>
				<li>
					Caddy:
					<pre><code>caddy run</code></pre>
				</li>
				<li>
					Redis:
					<pre><code>redis-server</code></pre>
				</li>
			</ul>
		</li>
		hcaptcha_key: str mail_address: str mail_password: str mail_username: str mail_server: str mail_port:
		int secret_key: str
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
		</li>
		<li>
			Start the server
			<ul>
				<li>
					Backend:
					<pre><code>pipenv run uvicorn classquiz:app --reload</code></pre>
				</li>
				<li>
					Frontend:
					<pre><code>cd frontend && pnpm dev</code></pre>
				</li>
			</ul>
		</li>
	</ul>

	<h2>BEFORE you submit a Pull-Request</h2>
	<h4>Frontend</h4>
	<p>Please format and lint your code with</p>
	<pre><code>pnpm run format && pnpm run lint</code></pre>

	<h4>Backend</h4>
	<p>IDK, just check that it works!</p>
</article>
