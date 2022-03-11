### Build Step
# pull the Node.js Docker image
ARG redis
FROM node:16 as builder
# ENV API_URL=http://api:80
ENV API_URL=https://mawoka.eu
ENV REDIS_URL=$REDIS
ENV VITE_SENTRY=https://4981de1f72f24fd7b5e21b8913b93a02@o661934.ingest.sentry.io/6254641
# change working directory
WORKDIR /usr/src/app

# copy the package.json files from local machine to the workdir in container
COPY package*.json ./

# run npm install in our local machine
RUN apt update && apt install -y curl && curl -f https://get.pnpm.io/v6.16.js | node - add --global pnpm && pnpm i

# copy the generated modules and all other files to the container
COPY . .

# build the application
RUN pnpm run build

### Serve Step
# pull the Node.js Docker image
FROM node:16

# change working directory
WORKDIR /app
RUN apt update && apt install -y curl && curl -f https://get.pnpm.io/v6.16.js  | node - add --global pnpm && apt purge curl -y && apt autoremove -y
# copy files from previous step
COPY --from=builder /usr/src/app/build .
COPY --from=builder /usr/src/app/package.json .
COPY --from=builder /usr/src/app/node_modules ./node_modules

# our app is running on port 3000 within the container, so need to expose it
EXPOSE 3000

# the command that starts our app
CMD ["pnpm", "run", "run:prod"]