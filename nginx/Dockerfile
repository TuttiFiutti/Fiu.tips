FROM nginx
RUN rm /etc/nginx/conf.d/default.conf
ARG SECRET_DIR=/etc/letsencrypt/live/fiu.tips/
RUN mkdir --parents /etc/letsencrypt/live/fiu.tips
RUN echo $SECRET_DIR
COPY $SECRET_DIR /etc/letsencrypt/live/fiu.tips/

COPY nginx/html /usr/share/nginx/html
COPY nginx/conf /etc/nginx