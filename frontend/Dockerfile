# /frontend/Dockerfile
FROM node:18-slim

WORKDIR /app

# Install Vue CLI globally
RUN npm install -g @vue/cli

# Copy package files from the current context (which is ./frontend)
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

EXPOSE 8080

CMD ["npm", "run", "serve"]