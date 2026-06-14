# --- STAGE 1: Build the Vue application ---
FROM node:18-slim AS build-stage

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY . .

# Run the production build command (generates the /dist folder)
RUN npm run build


# --- STAGE 2: Serve the app with Nginx ---
FROM nginx:alpine AS production-stage

# Copy the compiled static HTML/JS/CSS files from Stage 1 into Nginx
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Tell Nginx to look at Render's dynamic $PORT environment variable 
# and start the server instead of a hardcoded port
CMD ["sh", "-c", "exec nginx -g 'daemon off;' -c /etc/nginx/nginx.conf -g 'listen 0.0.0.0:'${PORT:-80}';'"]