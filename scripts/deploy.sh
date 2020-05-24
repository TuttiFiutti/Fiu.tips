cd frontend && npm run build && cd dist && \
cp -rf . ../../nginx/html && \
cd ../../ && \
rsync -avz .env_prod docker-compose.yaml backend nginx oauth touchstone@fiu.tips:~/Fiutips && \
ssh touchstone@fiu.tips "cd Fiutips && mv .env_prod .env && docker-compose up -d --build"