# nexus.connect

This is the nexus_connect project.

## Getting Started

```bash
# Clone the repository:

git clone https://github.com/Fayord/nexus_connect.git
cd external/chroma
git submodule init
git submodule update


# move to root

cd ../..

# copy .credential.example to .credential

cp .credential.example .credential

# add your openai api key

docker-compose up -d --build

# open data_folder/preprocessing/digest.ipynb jupyter notebook then run all cells

# and read the last cell if everything correct

# it will create folder in ./external/chroma/"chroma" this folder contain vector data

# TODO: change ./external/chroma/"chroma" to -> ./vector_db/chroma on root folder

cd tests/

# it should return result of dimension of washing machine

python test_200.py
```
