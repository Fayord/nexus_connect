# nexus.connect

This is the nexus_connect project.

## Getting Started

```bash
# Install Milvus Standalone with Docker Compose (CPU)
# https://milvus.io/docs/install_standalone-docker.md #version 2.3.x
mkdir milvus_database
cd milvus_database
wget https://github.com/milvus-io/milvus/releases/download/v2.3.1/milvus-standalone-docker-compose.yml -O docker-compose.yml

sudo docker-compose up -d


cd ..

# Clone the repository:

git clone https://github.com/Fayord/nexus_connect.git

cd nexus_connect

# copy .env.example to .env

cp .env.example .env

# add your openai api key

# download docker image from this
# https://drive.google.com/drive/folders/1lkxjSAwOAXWgh0Zl_YsaxlJFplw90goz?usp=drive_link

docker load -i image_2023_10_19.tar

docker run --env-file=.env -it --rm -p 9300:9300 naxon-chatbot-api

# then add data by test_add_website_data.py
cd tests
python test_add_website_data.py

# then ask birthday of aum
python test_200.py
```
