### Build Step
# pull the Node.js Docker image
FROM node:17.8-bullseye as builder
# ENV API_URL=http://api:80
ENV API_URL=https://mawoka.eu
#ENV REDIS_URL=rediss://red-cahmuvjru51oehk07dgg:WTYwEKUavJmUamj0OgB7QqACKMKNXrDY@frankfurt-redis.render.com:6379
ENV REDIS_URL=redis://localhost:6379
ENV VITE_MAPBOX_ACCESS_TOKEN=pk.eyJ1IjoibWF3b2thIiwiYSI6ImNsMjBob3d4ZjBhcGszYnE0bWp4aXB1ZW4ifQ.IByxV1qeIuEWpHCWsuB88A
# This Mapbox-token is restricted to the following urls: classquiz.de, classquiz.mawoka.eu, test.com
ENV VITE_HCAPTCHA=ee81b2a1-acf3-4d20-b2a4-a7ea94c7eba5
ENV VITE_SENTRY=https://75cb4ef1be624d8f81bbaf864b722f8a@glitch.mawoka.eu/2
# change working directory
WORKDIR /usr/src/app


# copy the package.json files from local machine to the workdir in container
COPY package*.json ./
COPY pnpm-lock.yaml ./

# run npm install in our local machine
RUN corepack enable && corepack prepare pnpm@7.0.0-rc.2 --activate && pnpm i

# copy the generated modules and all other files to the container
COPY . .

RUN apt update && \
    apt install -y redis-server

# build the application
RUN nohup bash -c "redis-server &" && sleep 4 && pnpm run build

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
