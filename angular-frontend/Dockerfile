FROM node:18-alpine as build 
WORKDIR /app
COPY package*.json ./ 
RUN npm install
COPY . /app
RUN npx ng build --configuration=production --source-map

FROM nginx:alpine

RUN mkdir -p /usr/share/nginx/html/angular/dist
COPY --from=build /app/dist/angular-frontend/browser*.map /usr/share/nginx/html/angular/dist/
COPY --from=build /app/dist/angular-frontend/browser /usr/share/nginx/html/angular

ARG DD_GIT_REPOSITORY_URL
ARG DD_GIT_COMMIT_SHA
ENV DD_GIT_REPOSITORY_URL=${DD_GIT_REPOSITORY_URL}
ENV DD_GIT_COMMIT_SHA=${DD_GIT_COMMIT_SHA}

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
