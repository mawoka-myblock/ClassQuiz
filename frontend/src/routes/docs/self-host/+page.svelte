<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
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
	<title>ClassQuiz/docs - Self-Host</title>
	<meta
		name="description"
		content="How to self-host ClassQuiz, the open-source quiz-application"
	/>
</svelte:head>
<article
	class="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto mt-10 prose-slate px-4 dark:prose-invert"
>
	<h1>Self-Hosting</h1>
	<p>Since ClassQuiz is open-source, it can also be self-hosted.</p>

	<h2>Warning</h2>
	<p>
		Although some versions are already released, <b>I</b> would recommend to run the latest
		commit (where checks pass) from the <b>master</b>-branch.
	</p>

	<h2>Requirements</h2>
	<h3>Software</h3>
	<ul>
		<li>
			<a href="https://docker.com" target="_blank">Docker</a> (<a
				href="https://docs.docker.com/compose/install/linux/"
				target="_blank">Compose</a
			>)
		</li>
		<li><a href="https://git-scm.com/" target="_blank">Git</a></li>
		<li>
			A <a href="https://redis.com" target="_blank">Redis</a>-Server
		</li>
	</ul>
	<h3>3rd-Parties</h3>
	<h4>Required</h4>
	<ul>
		<li><a href="https://hcaptcha.com">hCaptcha (Captcha)</a></li>
		<li><a href="https://www.mapbox.com/">Mapbox (Maps)</a></li>
	</ul>
	<h4>Optional</h4>
	<ul>
		<li><a href="https://sentry.io">Sentry (Error-Logging)</a></li>
		<li>
			<a href="https://console.cloud.google.com/apis/dashboard"
				>Google-Credentials (Sign-In)</a
			>
		</li>
		<li><a href="https://github.com/settings/developers">GitHub-Credentials (Sign-In)</a></li>
	</ul>

	<h2>Installation</h2>
	<p>At first, clone the repo:</p>

	<pre><code class="language-bash"
			>git clone https://github.com/mawoka-myblock/classquiz && cd ClassQuiz</code
		></pre>
	<p>
		Now, you'll configure your frontend. You'll have to change the following in <code
			>frontend/Dockerfile</code
		>:
	</p>
	<ul>
		<li><code>VITE_MAPBOX_ACCESS_TOKEN</code>: A Mapbox-token which is optional.</li>
		<li><code>VITE_HCAPTCHA</code>: The hCaptcha-Siteky for captchas</li>
		<li>
			<code>VITE_CAPTCHA_ENABLED</code>: Set it to <code>true</code>, if the captcha should be
			available
		</li>
		<li><code>VITE_SENTRY</code>: A Sentry-DSN for Sentry (optional)</li>
		<li>
			<code>VITE_GOOGLE_AUTH_ENABLED</code>: Set it to <code>true</code>, if Google-Auth is
			set up. Otherwise, leave it unset.
		</li>
		<li>
			<code>VITE_GITHUB_AUTH_ENABLED</code>: Set it to <code>true</code>, if GitHub-Auth is
			set up. Otherwise, leave it unset.
		</li>
	</ul>

	<h2>Configuration</h2>
	<h3>Storage Provider</h3>
	<p>
		You'll have to set up a storage provider for some pictures (these getting imported from
		Kahoot!). For now, you can use <a href="https://min.io/" target="_blank">Minio (S3)</a> or
		the local filesystem. Please not that I'd recommend Minio for larger instances, since it can
		be scaled and the media doesn't have to streamed through the (comparatively) slow ClassQuiz
		server. Now, that you've decided on a storage backend, you can set the
		<code>STORAGE_BACKEND</code>-environment-variable to either <code>s3</code> or
		<code>local</code>. If you ask yourself what happened with deta, I've decided to remove it,
		since the went all-in with their spaces and I think that hardly anyone used it anyway.
	</p>
	<h4>If you chose Minio (S3)...</h4>
	<p>
		...you'll also have to set the <code>S3_ACCESS_KEY</code>, <code>S3_SECRET_KEY</code> and
		the
		<code>S3_BASE_URL</code>. The <code>S3_BUCKET_NAME</code> can also be set, but defaults to
		<code>classquiz</code>.
	</p>
	<h4>If you chose the local filesystem...</h4>
	<p>
		...you'll have to set the <code>STORAGE_PATH</code> environment variable. The path must be
		absolute (so start with a <code>/</code>).
	</p>
	<p>
		Before you can start your stack, you have to set some environment-variables in your
		<code>docker-compose.yml</code>.
	</p>
	<h3>GitHub/Google-Auth</h3>
	<p>
		This step is purely optional, but it will enable users to log in using their
		Google/GitHub-accounts.
	</p>
	<h4>Google</h4>
	<p>
		First, go to <a href="https://console.cloud.google.com/apis/dashboard"
			>console.cloud.google.com/apis/dashboard</a
		> and create a new project and select it. Then, go to the "OAuth consent screen" and set it up.
		Next, go to the "Credentials"-tab and click on "Create Credentials" and create a new "OAuth Client
		ID". This ID should be from the application-type "Web application". Afterwards, add a new "Authorised
		JavaScript origin", which is just the base-domain (with https) of your ClassQuiz-installation.
		Then, add a new "Authorised redirect URI". This URI will have the following scheme:
	</p>
	<pre><code>https://[BASE_URL]/api/v1/users/oauth/google/auth</code></pre>
	<p>You're done! Not the client-secret and the client-id down, you'll need it later.</p>

	<h4>GitHub</h4>
	<p>
		First, go to <a href="https://github.com/settings/developers"
			>github.com/settings/developers</a
		> and create a "new OAuth App". The "Authorization callback URL" has the following schema:
	</p>
	<pre><code>https://[BASE_URL]/api/v1/users/oauth/github/auth</code></pre>
	<p>
		That's it. Click on "Register application" and generate a new client secret and save it for
		later, together with your client-id.
	</p>

	<h3>Docker-Compose File</h3>
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
	  REDIS_URL: redis://redis:6379/0?decode_responses=True # don't change
      API_URL: http://api:80 # don't change
  api:
    build: &build_cfg
      context: .
      dockerfile: Dockerfile
    restart: &restart always
    depends_on: &depends
      - db
      - redis

    environment: &env_vars
      ROOT_ADDRESS: "https://classquiz.de" # Base-URL (change it)
      DB_URL: "postgresql://postgres:classquiz@db:5432/classquiz" # don't change
      MAIL_ADDRESS: "classquiz@mawoka.eu" # Email-Address (change it)
      MAIL_PASSWORD: "MAIL_PASSWORD" # Email-Password (change it)
      MAIL_USERNAME: "classquiz@mawoka.eu" # Email-Username (change it)
      MAIL_SERVER: "smtp.gmail.com" # SMTP-Server (change it)
	  MAIL_PORT: "587" # SMTP-Port
	  SKIP_EMAIL_VERIFICATION: True # Set this to skip sending emails
      MAX_WORKERS: "1" # Very important and don't change it!
      REDIS: "redis://redis:6379/0?decode_responses=True" # don't change
      SECRET_KEY: "TOP_SECRET" # openssl rand -hex 32
	  MEILISEARCH_URL: "http://meilisearch:7700" # don't change
      ACCESS_TOKEN_EXPIRE_MINUTES: 30 # don't change
      HCAPTCHA_KEY: "" # Private hCaptcha key for verification (change it)
	  STORAGE_BACKEND: "local" # MUST BE EITHER "s3" OR "local"
	  FREE_STORAGE_LIMIT: "1074000000" # Free storage limit in bytes (default: 1GB)

	  # If STORAGE_BACKEND is "s3"
	  S3_ACCESS_KEY=YOUR_ACCESS_KEY
	  S3_SECRET_KEY=YOUR_SECRET_KEY
	  S3_BASE_URL=YOUR_S3_BASE_URL

	  # If STORAGE_BACKEND is "local"
	  STORAGE_PATH: "/var/storage"

	  # GOOGLE_AUTH
      GOOGLE_CLIENT_ID: # Your Google-Client ID, or leave it unset if you don't want it.
      GOOGLE_CLIENT_SECRET: # Your Google-Client Secret, or leave it unset if you don't want it.

	  # GITHUB_AUTH
	  GITHUB_CLIENT_ID: # Your GitHub-Client ID, or leave it unset if you don't want it.
      GITHUB_CLIENT_SECRET: # Your GitHub-Client Secret, or leave it unset if you don't want it.

    volumes: # Only needed if you chose the "local" storage-backend
	  - ./uploads:/var/storage

  redis:
    image: redis:alpine
    restart: always
    healthcheck:
      test: [ "CMD", "redis-cli","ping" ]

  db:
    image: postgres:14-alpine
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

  meilisearch:
    image: getmeili/meilisearch:latest
    restart: always
    environment:
      MEILI_NO_ANALYTICS: true
    volumes:
      - meilisearch-data:/data.ms
  worker:
    build: *build_cfg
    environment: *env_vars
    restart: *restart
    depends_on: *depends
    command: arq classquiz.worker.WorkerSettings


volumes:
  data:
  meilisearch-data:
	</code></pre>
	<p>Run the following command to generate and set the secret up automatically</p>
	<pre><code class="language-bash"
			>sed -i "s/TOP_SECRET/$(openssl rand -hex 32)/g" docker-compose.yml</code
		></pre>
	<p>Now build and deploy:</p>
	<pre><code>docker compose build && docker compose up -d</code></pre>
	<p><b>ClassQuiz needs HTTPS/SSL to work properly!</b></p>
	<p><b>Enjoy! ❤️</b></p>
</article>
