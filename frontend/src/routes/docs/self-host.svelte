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
		<li><a href="https://docker.com">Docker</a></li>
		<li><a href="https://git-scm.com/">Git</a></li>
		<li>
			A <a href="https://redis.com">Redis</a>-Server
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
	<p>Now, you'll configure your frontend. You'll have to change the following:</p>
	<ul>
		<li><code>VITE_MAPBOX_ACCESS_TOKEN</code>: A Mapbox-token which is optional.</li>
		<li><code>VITE_HCAPTCHA</code>: The hCaptcha-Siteky for captchas</li>
		<li><code>VITE_SENTRY</code>: A Sentry-DSb for Sentry (optional)</li>
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
		KAHOOT!). For now, you can use <a href="https://deta.sh">Deta</a> or the local filesystem.
		Please note that I would <b>NOT</b> use the local file system because of
		<a href="https://wiki.owasp.org/index.php/Path_Traversal">Path Traversals</a>. I tried to
		prevent these attacks, but I really wouldn't trust it, because it's a regex! You'll have to
		set the
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
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - db
      - redis

    environment:
      ROOT_ADDRESS: "https://classquiz.mawoka.eu" # Base-URL (change it)
      DB_URL: "postgresql://postgres:classquiz@db:5432/classquiz" # don't change
      MAIL_ADDRESS: "classquiz@mawoka.eu" # Email-Address (change it)
      MAIL_PASSWORD: "MAIL_PASSWORD" # Email-Password (change it)
      MAIL_USERNAME: "classquiz@mawoka.eu" # Email-Username (change it)
      MAIL_SERVER: "smtp.gmail.com" # SMTP-Server (change it)
	  MAIL_PORT: "587" # SMTP-Port
      MAX_WORKERS: "1" # Very important and don't change it!
      REDIS: "redis://redis:6379/0?decode_responses=True" # don't change
      SECRET_KEY: "TOP_SECRET" # openssl rand -hex 32
	  MEILISEARCH_URL: "http://meilisearch:7700" # don't change
      ACCESS_TOKEN_EXPIRE_MINUTES: 30 # don't change
      HCAPTCHA_KEY: "" # Private hCaptcha key for verification (change it)
	  STORAGE_BACKEND: "deta" # MUST BE EITHER "deta" OR "local"

	  # If STORAGE_BACKEND is "deta"
	  DETA_PROJECT_KEY: "YOUR_DETA_PROJECT_KEY"
	  DETA_PROJECT_ID: "YOUR_DETA_PROJECT_ID"

	  # If STORAGE_BACKEND is "local"
	  STORAGE_PATH: "/var/storage"

	  # GOOGLE_AUTH
      GOOGLE_CLIENT_ID: # Your Google-Client ID, or leave it unset if you don't want it.
      GOOGLE_CLIENT_SECRET: # Your Google-Client Secret, or leave it unset if you don't want it.

	  # GITHUB_AUTH
	  GITHUB_CLIENT_ID: # Your GitHub-Client ID, or leave it unset if you don't want it.
      GITHUB_CLIENT_SECRET: # Your GitHub-Client Secret, or leave it unset if you don't want it.


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

  meilisearch:
    image: getmeili/meilisearch:latest
    restart: always
    environment:
      MEILI_NO_ANALYTICS: true
    volumes:
      - meilisearch-data:/data.ms
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
	<p>You'll have to create an index in Meilisearch with the following command:</p>
	<pre><code>docker compose exec api python3 import_to_meili.py</code></pre>
	<p>Note: I would recommend to add the command from above to your crontab so it runs daily.</p>
	<p><b>Enjoy! ❤️</b></p>
</article>
