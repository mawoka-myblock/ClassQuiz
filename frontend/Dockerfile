### Build Step
# pull the Node.js Docker image
FROM node:17.8-bullseye as builder
# ENV API_URL=http://api:80
ENV API_URL=https://mawoka.eu
ENV REDIS_URL=CHANGE_ME
ENV VITE_MAPBOX_ACCESS_TOKEN=pk.eyJ1IjoibWF3b2thIiwiYSI6ImNsMjBob3d4ZjBhcGszYnE0bWp4aXB1ZW4ifQ.IByxV1qeIuEWpHCWsuB88A
# This Mpbox-token is restricted to the following urls: classquiz.de, classquiz.mawoka.eu, test.com
ENV VITE_HCAPTCHA=ee81b2a1-acf3-4d20-b2a4-a7ea94c7eba5
ENV VITE_SENTRY=https://4981de1f72f24fd7b5e21b8913b93a02@o661934.ingest.sentry.io/6254641
# change working directory
WORKDIR /usr/src/app

# copy the package.json files from local machine to the workdir in container
COPY package*.json ./
COPY pnpm-lock.yaml ./

# run npm install in our local machine
RUN corepack enable && corepack prepare pnpm@7.0.0-rc.2 --activate && pnpm i

# copy the generated modules and all other files to the container
COPY . .

# build the application
RUN pnpm run build

### Serve Step
# pull the Node.js Docker image
FROM node:17.8-bullseye-slim

# change working directory
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@7.0.0-rc.2 --activate && pnpm i
# copy files from previous step
COPY --from=builder /usr/src/app/build .
COPY --from=builder /usr/src/app/package.json .
COPY --from=builder /usr/src/app/pnpm-lock.yaml .
COPY --from=builder /usr/src/app/node_modules ./node_modules

# our app is running on port 3000 within the container, so need to expose it
EXPOSE 3000

# the command that starts our app
CMD ["pnpm", "run", "run:prod"]