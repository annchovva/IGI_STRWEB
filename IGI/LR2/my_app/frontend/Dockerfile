FROM node:16
WORKDIR /app
COPY package.json ./
RUN npm cache clean --force && npm install --legacy-peer-deps
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
