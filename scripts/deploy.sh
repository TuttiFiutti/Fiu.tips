cd frontend && npm run build && cd dist && \
cp -rf . ../../nginx/html && \
cd ../../ && \
rsync -avz .env docker-compose.yaml backend nginx oauth touchstone@fiu.tips:~/Fiutips && \
ssh touchstone@fiu.tips "cd Fiutips && docker-compose up -d --build"