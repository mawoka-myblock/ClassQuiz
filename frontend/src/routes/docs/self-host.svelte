<script lang='ts'>
	import { onMount } from 'svelte';
	import '$lib/hljs.css';

	onMount(async () => {
		const { default: hljs } = await import('highlight.js/lib/common');
		hljs.highlightAll();
	});
</script>

<svelte:head>
	<title>ClassQuiz/docs - Self-Host</title>
	<meta
		name='description'
		content='How to self-host ClassQuiz, the open-source quiz-application'
	/>
</svelte:head>
<article
	class='prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto mt-10 prose-pink text-yellow-50 px-4'
>
	<h1>Self-Hosting</h1>
	<p>Since ClassQuiz is open-source, it can also be self-hosted.</p>


	<h2>Warning</h2>
	<p>This "warning" is just temporary, because you need a <a href='https://deta.sh'>Deta</a> account (which is free)
		to store and serve the images getting imported with the kahoot-import function. I am planning to add more backends like s3 or the local file system. Untill then, Deta is needed. </p>

	<h2>Requirements</h2>
	<ul>
		<li><a href='https://docker.com'>Docker</a></li>
		<li><a href='https://git-scm.com/'>Git</a></li>
		<li>
			A <a href='https://redis.com'>Redis</a>-Server (I recommend
			<a href='https://upstash.com'>Upstash</a>)
		</li>
	</ul>

	<h2>Installation</h2>
	<p>At first, clone the repo:</p>

	<pre><code class='language-bash'
	>git clone https://github.com/mawoka-myblock/classquiz && cd ClassQuiz</code
	></pre>
	<p>
		Now, set a <b>VALID</b> Redis-URI in <code>frontend/Dockerfile</code> and, if you want Sentry,
		set a valid Sentry-DSN.
	</p>
	<p>
		You must set a valid hCaptcha-Sitekey in the <code>frontend/Dockerfile</code>.
	</p>

	<h2>Configuration</h2>
	<p>
		Before you can start your stack, you have to set some environment-variables in your
		<code>docker-compose.yml</code>.
	</p>
	<pre><code class='language-yaml'
	>version: "3"

services:
  frontend:
    restart: always
    build:
      context: ./frontend
      dockerfile: Dockerfile
    depends_on:
      - redis
      - api
    environment:
      REDIS_URL: redis://redis:6379/0?decode_responses=True # For runtime
      API_URL: http://api:80 # For runtime
  api:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - db
      - redis

    environment:
      ROOT_ADDRESS: "https://classquiz.mawoka.eu" # Base-URL
      DB_URL: "postgresql://postgres:classquiz@db:5432/classquiz"
      MAIL_ADDRESS: "classquiz@mawoka.eu" # Email-Address
      MAIL_PASSWORD: "MAIL_PASSWORD" # Email-Password
      MAIL_USERNAME: "classquiz@mawoka.eu" # Email-Username
      MAIL_SERVER: "smtp.gmail.com" # SMTP-Server
      MAX_WORKERS: "1" # Very important and don't change it!
      MAIL_PORT: "587" # SMTP-Port
      REDIS: "redis://redis:6379/0?decode_responses=True" # decode_response is important!
      SECRET_KEY: "ghfvfgjgvjgvbh" # openssl rand -hex 32
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      HCAPTCHA_KEY: "" # Private hCaptcha key for verification
  redis:
    image: redis:alpine
    restart: always
    healthcheck:
      test: [ "CMD", "redis-cli","ping" ]

  db:
    image: postgres:alpine
    restart: always
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U postgres" ]
      interval: 5s
      timeout: 5s
      retries: 5
    environment:
      POSTGRES_PASSWORD: "classquiz"
      POSTGRES_DB: "classquiz"

    volumes:
      - data:/var/lib/postgresql/data
  proxy:
    image: caddy:alpine
    restart: always
    volumes:
      - ./Caddyfile-docker:/etc/caddy/Caddyfile
    ports:
      - "8000:8080" # Adjust the 8000 to your needs

volumes:
  data:
	</code></pre>
	<p>Now build and deploy:</p>
	<pre><code class='language-bash'>docker compose build && docker compose up -d</code></pre>
</article>
