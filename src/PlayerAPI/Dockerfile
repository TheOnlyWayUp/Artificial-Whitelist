# https://nodejs.org/en/docs/guides/nodejs-docker-webapp/

FROM node:16

# Create app directory
WORKDIR /src

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json ./
COPY config.json /config.json

RUN npm install
# If you are building your code for production
# RUN npm ci --only=production

ENV PLAYER_API_CONFIG_FILE=/config.json
ENV NODE_ENV=production

# Bundle app source
WORKDIR /src
COPY src .

CMD [ "node", "index.js" ]