# not using 20.3 since it has a bug on Macs : https://github.com/nodejs/docker-node/issues/1912
FROM node:20.2.0-slim

WORKDIR /work
RUN yarn
CMD ["yarn", "dev", "--host", "0.0.0.0"]