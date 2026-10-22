# Build from the repo root with: context: .. and dockerfile: lab3/frontend/Dockerfile
# Does NOT modify the existing client/Dockerfile used in lab 2.
FROM node:22-alpine AS build
WORKDIR /app
COPY client/package*.json ./
RUN npm ci
COPY client/ ./
RUN npm run build

FROM nginx:alpine
COPY lab3/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY lab3/frontend/proxy_params_lab3 /etc/nginx/proxy_params_lab3
COPY --from=build /app/dist/ /usr/share/nginx/html/
EXPOSE 80
