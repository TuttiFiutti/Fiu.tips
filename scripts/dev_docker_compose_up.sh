cd frontend && npm run build && cd dist && \
cp -rf . ../../nginx/html && \
cd ../../ && \
docker-compose up -d
