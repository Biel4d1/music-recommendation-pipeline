# Music Emotion Engine & Recommendation Pipeline

Este é um pipeline de dados ponta a ponta (End-to-End ETL) e um motor de recomendação baseado em Machine Learning, desenvolvido para rodar localmente. O sistema extrai metadados de faixas de playlists do Spotify, processa e categoriza as músicas em quadrantes emocionais com base no Modelo Circunplexo de Afeto de Russell, armazena os dados estruturados em um banco de dados SQLite local e realiza recomendações utilizando o algoritmo k-Nearest Neighbors ($k$-NN).

---

## 🛠️ Arquitetura do Sistema

O projeto é dividido em três etapas principais:

1. **Pipeline de Ingestão (`pipeline.py`)**: Conecta-se à API do Spotify via `spotipy` usando fluxo de autorização OAuth para recuperar metadados de playlists públicas ou privadas. O pipeline simula vetores de características de áudio (Valência, Energia, Tempo e Modo) de forma determinística devido às recentes depreciações da API pública do Spotify, organizando tudo em um banco de dados relacional local (`music_data.db`).
2. **Camada de Armazenamento (`music_data.db`)**: Banco de dados SQLite contendo a tabela estruturada `track_analytics` com chaves primárias definidas para evitar duplicidade de registros.
3. **Motor de Recomendação (`recommender.py`)**: Normaliza as features numéricas em uma escala de 0 a 1 usando `MinMaxScaler` e aplica o algoritmo de vizinhos mais próximos ($k$-NN) com distância Euclidiana para encontrar as faixas geometricamente mais próximas no espaço vetorial 3D.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Sistema Operacional (desenvolvido e testado em Arch Linux)
* Python 3.10+
* Chaves de API do Spotify (Client ID e Client Secret) obtidas no [Spotify Developer Dashboard](https://developer.spotify.com/)

### 1. Clonar o repositório e configurar o ambiente

# Clonar o repositório (via SSH)
git clone git@github.com:Biel4d1/music-recommendation-pipeline.git
cd music-recommendation-pipeline

# Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Instalar as dependências
pip install -r requirements.txt

2. Configurar as variáveis de ambiente

Crie um arquivo .env na raiz do projeto com as suas credenciais do Spotify:


export SPOTIFY_CLIENT_ID="seu_client_id_aqui"
export SPOTIFY_CLIENT_SECRET="seu_client_secret_aqui"
export SPOTIFY_REDIRECT_URI="[http://127.0.0.1:8080](http://127.0.0.1:8080)"

Carregue as variáveis no terminal:


source .env

3. Executar a Ingestão de Dados

Para buscar as faixas da sua playlist e carregar o banco de dados:


python pipeline.py

4. Executar o Sistema de Recomendação

Para buscar recomendações de faixas similares em seu banco de dados local:


python recommender.py

📊 Tecnologias Utilizadas

    Linguagem: Python

    APIs & Integrações: Spotipy (Spotify Web API Wrapper)

    Banco de Dados: SQLite3

    Machine Learning & Processamento de Dados: Scikit-Learn (NearestNeighbors, MinMaxScaler), Pandas


Salve e saia do nano (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

### Passo 3: Adicionar ao Git e Enviar para o GitHub

Agora que ambos os arquivos foram gerados, use a sua conexão SSH ativa para subir tudo de uma vez:

# Adicionar os novos arquivos ao rastreamento
git add requirements.txt README.md

# Confirmar as alterações localmente
git commit -m "docs: add Portuguese README and project requirements"

# Enviar as alterações para o repositório remoto
git push origin main
