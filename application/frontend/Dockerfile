FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN sed -i 's,/run/nginx.pid,/tmp/nginx.pid,g' /etc/nginx/nginx.conf && \
    touch /run/nginx.pid && \
    chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/run /run/nginx.pid && \
    chmod -R 755 /usr/share/nginx/html
USER nginx
EXPOSE 80
