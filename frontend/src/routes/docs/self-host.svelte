<script lang="ts">
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
		name="description"
		content="How to self-host ClassQuiz, the open-source quiz-application"
	/>
</svelte:head>
<article class="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto mt-10 prose-gray px-4">
	<h1>Self-Hosting</h1>
	<p>Since ClassQuiz is open-source, it can also be self-hosted.</p>

	<h2>Warning</h2>
	<p>
		Since ClassQuiz is in pretty early development, breaking changes come and go! Please check
		these docs again before updating your instance. I may also add more dependencies like <a
			href="https://typesense.org/">Typesense</a
		>
		ore something similar in the future, but I'll always provide a
		<code>docker-compose.yml</code> file, so the self-hosting process is still easy.
	</p>

	<h2>Requirements</h2>
	<ul>
		<li><a href="https://docker.com">Docker</a></li>
		<li><a href="https://git-scm.com/">Git</a></li>
		<li>
			A <a href="https://redis.com">Redis</a>-Server (I recommend
			<a href="https://upstash.com">Upstash</a>)
		</li>
	</ul>

	<h2>Installation</h2>
	<p>At first, clone the repo:</p>

	<pre><code class="language-bash"
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
	<h3>Storage Provider</h3>
	<p>
		You'll have to set up a storage provider for some pictures (these getting imported from
		KAHOOT!). For now, you can use <a href="https://deta.sh">Deta</a> or the local filesystem.
		Please note that I would <b>NOT</b> use the local file system because of these funny
		path-things. I tried to prevent these attacks, but i really wouldn't trust it. You'll have
		to set the
		<code>STORAGE_BACKEND</code>-environment-variable to either <code>deta</code> or
		<code>local</code>.
	</p>
	<h4>If you chose Deta...</h4>
	<p>
		...you'll also have to set the <code>DETA_PROJECT_KEY</code> and the
		<code>DETA_PROJECT_ID</code>.
	</p>
	<h4>If you chose the local filesystem...</h4>
	<p>
		...you'll have to set the <code>STORAGE_PATH</code> enviromnent variable. The path must be
		absolute (so start with a <code>/</code>).
	</p>
	<p>
		Before you can start your stack, you have to set some environment-variables in your
		<code>docker-compose.yml</code>.
	</p>
	<pre><code class="language-yaml"
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
	  STORAGE_BACKEND: "deta" # MUST BE EITHER "deta" OR "local"

	  # If STORAGE_BACKEND is "deta"
	  DETA_PROJECT_KEY: "YOUR_DETA_PROJECT_KEY"
	  DETA_PROJECT_ID: "YOUR_DETA_PROJECT_ID"

	  # If STORAGE_BACKEND is "local"
	  STORAGE_PATH: "/var/storage"
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
	<pre><code class="language-bash">docker compose build && docker compose up -d</code></pre>
</article>
