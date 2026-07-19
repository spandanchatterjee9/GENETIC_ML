FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend templates and static assets into default nginx serve path
COPY ./templates/ /usr/share/nginx/html/
COPY ./static/ /usr/share/nginx/html/static/

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
