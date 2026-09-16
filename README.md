# 🌦️ Weather Data Pipeline — ETL com Airflow, Docker e MySQL

![Python](https://img.shields.io/badge/Python-Data%20Engineering-blue?logo=python&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-3.1.7-017CEE?logo=apacheairflow&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-ETL%20Target-4479A1?logo=mysql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Transform-150458?logo=pandas&logoColor=white)

Pipeline de Engenharia de Dados responsável por **extrair dados meteorológicos da API OpenWeatherMap, transformar os dados com Pandas e carregá-los em um banco MySQL/MariaDB**, utilizando **Apache Airflow** para orquestração e **Docker** para containerização do ambiente.

O projeto coleta dados meteorológicos da cidade do **Rio de Janeiro — RJ** e mantém um histórico das condições climáticas para futuras análises.

---

## 🎯 Objetivo

O objetivo deste projeto é aplicar, na prática, conceitos fundamentais de Engenharia de Dados:

- Construção de pipelines **ETL**
- Consumo de APIs REST
- Tratamento de JSON
- Manipulação e transformação de dados com Pandas
- Persistência de dados em banco relacional
- Orquestração com Apache Airflow
- Criação e gerenciamento de DAGs
- Containerização com Docker
- Gerenciamento de dependências
- Variáveis de ambiente e credenciais
- Logging e tratamento de falhas
- Comunicação entre containers e serviços externos
- Tratamento de mudanças de schema em APIs

---

## 🏗️ Arquitetura

```mermaid
flowchart LR

    API[🌐 OpenWeatherMap API]

    E[📥 Extract]
    JSON[(📄 JSON Raw)]
    T[🔄 Transform<br/>Pandas]
    PQ[(📦 Parquet)]
    L[📤 Load<br/>SQLAlchemy + PyMySQL]
    MYSQL[(🐬 MySQL / MariaDB)]

    AF[⚙️ Apache Airflow]

    API --> E
    E --> JSON
    JSON --> T
    T --> PQ
    PQ --> L
    L --> MYSQL

    AF -. Orquestra .-> E
    AF -. Orquestra .-> T
    AF -. Orquestra .-> L
```

O fluxo principal é:

```text
OpenWeatherMap API
        ↓
     Extract
        ↓
       JSON
        ↓
   Transformação
      Pandas
        ↓
      Parquet
        ↓
       Load
        ↓
 MySQL / MariaDB
```

O **Apache Airflow** é responsável por orquestrar todas essas etapas.

---

## ⚙️ Infraestrutura do Airflow

O ambiente do Airflow é executado através do Docker Compose.

```text
Docker Compose
│
├── Airflow API Server
├── Airflow Scheduler
├── Airflow Worker
├── Airflow Triggerer
├── Airflow DAG Processor
│
├── Redis
│   └── Broker do Celery
│
└── PostgreSQL
    └── Metadata Database do Airflow
```

> **Importante:** o PostgreSQL presente no Docker Compose é utilizado apenas internamente pelo Airflow para armazenar metadados como DAG Runs, Tasks e estados de execução.

Os **dados meteorológicos da pipeline são armazenados em MySQL/MariaDB**.

---

# 🔄 Pipeline ETL

## 📥 1. Extract

Arquivo:

```text
src/extract_data.py
```

A etapa de extração realiza uma requisição HTTP para a API do **OpenWeatherMap**.

Os dados retornados são armazenados inicialmente em:

```text
data/weather_data.json
```

Exemplos de informações coletadas:

- temperatura
- sensação térmica
- temperatura mínima e máxima
- umidade
- pressão atmosférica
- velocidade e direção do vento
- quantidade de nuvens
- precipitação
- nascer e pôr do sol
- latitude e longitude
- descrição das condições climáticas

---

## 🔄 2. Transform

Arquivo:

```text
src/transform_data.py
```

O JSON retornado pela API é transformado utilizando **Pandas**.

Entre as transformações realizadas estão:

- Conversão do JSON para DataFrame
- Normalização de objetos aninhados
- Tratamento da estrutura `weather`
- Remoção de colunas desnecessárias
- Renomeação e padronização de colunas
- Conversão de Unix Timestamp
- Conversão para o timezone `America/Sao_Paulo`
- Tratamento de campos opcionais da API

Exemplo:

```text
main.temp       → temperature
main.humidity   → humidity
coord.lon       → longitude
coord.lat       → latitude
rain.1h         → rain_1h
sys.sunrise     → sunrise
sys.sunset      → sunset
```

A coluna `weather`, que originalmente contém uma lista de objetos JSON, também é normalizada para:

```text
weather_id
weather_main
weather_description
```

---

## 📦 Comunicação entre Tasks

Após a transformação, o DataFrame é temporariamente salvo em formato **Parquet**:

```text
/opt/airflow/data/tmp_data.parquet
```

O arquivo é utilizado para transportar os dados entre as tasks:

```text
transform
   ↓
Parquet
   ↓
 load
```

Isso evita depender da serialização direta de DataFrames entre Tasks do Airflow e preserva os tipos dos dados.

---

## 📤 3. Load

Arquivo:

```text
src/load_data.py
```

A conexão com o banco é realizada utilizando:

- SQLAlchemy
- PyMySQL

Connection string:

```text
mysql+pymysql://usuario:senha@host:3306/database
```

O DataFrame é carregado na tabela:

```text
rj_weather
```

utilizando:

```python
df.to_sql(
    name="rj_weather",
    con=engine,
    if_exists="append",
    index=False
)
```

O modo `append` permite criar um histórico das coletas realizadas ao longo do tempo.

---

# ⚡ Apache Airflow

A DAG está localizada em:

```text
dags/weather_dag.py
```

e possui três Tasks:

```text
┌─────────┐     ┌───────────┐     ┌──────┐
│ extract │ ──→ │ transform │ ──→ │ load │
└─────────┘     └───────────┘     └──────┘
```

A DAG é executada **a cada hora**.

Além disso, possui:

```text
Retries:       2
Retry delay:   5 minutos
Catchup:       False
```

Assim, falhas temporárias de rede ou API podem ser automaticamente retentadas pelo Airflow.

---

# 🛠️ Stack

| Tecnologia | Utilização |
|---|---|
| **Python** | Desenvolvimento do pipeline |
| **Pandas** | Transformação dos dados |
| **Requests** | Consumo da API |
| **OpenWeatherMap** | Fonte dos dados |
| **Apache Airflow 3** | Orquestração |
| **Docker** | Containerização |
| **Docker Compose** | Orquestração dos containers |
| **MySQL / MariaDB** | Armazenamento dos dados meteorológicos |
| **SQLAlchemy** | Abstração da conexão SQL |
| **PyMySQL** | Driver MySQL |
| **PostgreSQL** | Metadata Database do Airflow |
| **Redis** | Broker do CeleryExecutor |
| **Parquet** | Comunicação entre as Tasks |
| **Jupyter Notebook** | Exploração e análise dos dados |
| **UV** | Gerenciamento de dependências Python |

---

# 📁 Estrutura do Projeto

```text
weather-data-pipeline-airflow/
│
├── dags/
│   └── weather_dag.py
│
├── src/
│   ├── extract_data.py
│   ├── transform_data.py
│   └── load_data.py
│
├── data/
│   ├── weather_data.json
│   └── tmp_data.parquet
│
├── config/
│   └── .env
│
├── notebooks/
│   └── analysis_data.ipynb
│
├── Dockerfile
├── docker-compose.yaml
├── main.py
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

> `config/.env`, dados temporários e outros arquivos sensíveis não devem ser versionados.

---

# 🔐 Variáveis de Ambiente

Crie:

```text
config/.env
```

Exemplo:

```env
API_KEY=SUA_OPENWEATHER_API_KEY

user=seu_usuario_mysql
password=sua_senha
database=youtube_weather_data
```

> ⚠️ Nunca faça commit de API Keys ou senhas no GitHub.

---

# 🐬 Configuração do MySQL

Crie o banco:

```sql
CREATE DATABASE youtube_weather_data
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Crie um usuário:

```sql
CREATE USER 'pipeline_user'@'%'
IDENTIFIED BY 'sua_senha';
```

Conceda acesso:

```sql
GRANT ALL PRIVILEGES
ON youtube_weather_data.*
TO 'pipeline_user'@'%';
```

Confira:

```sql
SHOW GRANTS FOR 'pipeline_user'@'%';
```

---

## 🐳 MySQL + Docker Desktop

Neste projeto, o Airflow roda dentro do Docker enquanto o banco MySQL/MariaDB pode rodar diretamente no host.

No Windows com Docker Desktop, o container acessa o host utilizando:

```text
host.docker.internal
```

Arquitetura:

```text
Airflow Worker
     Docker
       │
       │ host.docker.internal:3306
       ▼
Windows Host
       │
       ▼
MySQL / MariaDB
       │
       ▼
youtube_weather_data
```

---

# 🚀 Executando o Projeto

## 1. Clone o repositório

```bash
git clone https://github.com/DevKneves/weather-data-pipeline-airflow.git

cd weather-data-pipeline-airflow
```

---

## 2. Configure sua API Key

Crie:

```text
config/.env
```

e adicione as credenciais necessárias.

Uma API Key gratuita pode ser obtida através do OpenWeatherMap.

---

## 3. Build da imagem do Airflow

```bash
docker compose build
```

O Dockerfile estende a imagem oficial do Airflow e adiciona suporte à comunicação com MySQL.

---

## 4. Inicialize o Airflow

Na primeira execução:

```bash
docker compose up airflow-init
```

Após a inicialização:

```bash
docker compose up -d
```

---

## 5. Verifique os containers

```bash
docker compose ps
```

---

## 6. Acesse o Airflow

Abra:

```text
http://localhost:8080
```

Credenciais padrão do ambiente de desenvolvimento:

```text
Usuário: airflow
Senha:   airflow
```

---

## 7. Execute a DAG

Localize:

```text
youtube_weather_pipeline
```

e execute manualmente através do botão **Trigger DAG**.

Após isso, o Airflow executará:

```text
extract
   ↓
transform
   ↓
load
```

---

# 🔎 Consultando os Dados

Após uma execução bem-sucedida:

```sql
USE youtube_weather_data;

SELECT *
FROM rj_weather
ORDER BY datetime DESC;
```

Para verificar a quantidade de registros:

```sql
SELECT COUNT(*)
FROM rj_weather;
```

---

# 🧪 Principais aprendizados

Durante o desenvolvimento deste projeto foram praticados conceitos como:

- Construção de ETL modular
- APIs REST
- JSON
- Pandas
- DataFrames
- SQL
- MySQL
- SQLAlchemy
- Docker
- Docker Compose
- Apache Airflow
- DAGs
- CeleryExecutor
- Redis
- Volumes Docker
- Networking entre host e container
- Variáveis de ambiente
- Logging
- Retentativas de Tasks
- Schema drift
- Persistência intermediária utilizando Parquet

Além da construção do pipeline, o projeto permitiu entender na prática a diferença entre:

```text
Banco da aplicação / dados
```

e:

```text
Metadata Database do orquestrador
```

---

# 🔀 Diferenças em relação ao projeto original

Este projeto foi desenvolvido como uma **adaptação de estudo** a partir do projeto prático apresentado pela engenheira de dados **Luiza (@vbluuiza)**.

A implementação original utiliza **PostgreSQL** como destino dos dados meteorológicos.

Nesta versão, optei por trabalhar com:

```text
MySQL / MariaDB
```

como banco de destino da pipeline.

Isso exigiu algumas adaptações, incluindo:

- utilização do driver **PyMySQL**
- utilização de `mysql+pymysql` no SQLAlchemy
- instalação do `apache-airflow-providers-mysql`
- criação de usuários e permissões específicas no MySQL
- comunicação entre Airflow/Docker e MySQL no host
- utilização de `host.docker.internal` no ambiente Windows
- adaptação do schema para MySQL
- armazenamento dos dados climáticos do **Rio de Janeiro**, em vez de São Paulo

O **PostgreSQL ainda está presente na infraestrutura**, mas somente como banco interno de metadados do Apache Airflow.

---

# 🙏 Créditos

Este projeto foi criado para fins de **estudo e prática de Engenharia de Dados** e teve como principal referência o projeto desenvolvido pela **Luiza (@vbluuiza)**.

### 📺 Canal

[@vbluuiza no YouTube](https://www.youtube.com/@vbluuiza)

### 🎥 Projeto prático / tutorial

[Pipeline ETL Weather Data](https://www.youtube.com/watch?v=I8qPqbXQBDU)

### 💻 Repositório original

[pipeline_etl_weather_data_tutorial_youtube](https://github.com/vbluuiza/pipeline_etl_weather_data_tutorial_youtube)

### 👩‍💻 GitHub da autora

[github.com/vbluuiza](https://github.com/vbluuiza/)

Agradeço à autora pelo conteúdo e pela disponibilização do projeto original, que serviu como base para estudo e desenvolvimento desta implementação.

---

# 👨‍💻 Autor

Desenvolvido e adaptado por **Kauã Neves**.

GitHub: [@DevKneves](https://github.com/DevKneves)

---

## ⭐ Sobre o projeto

Este repositório faz parte dos meus estudos em **Engenharia de Dados**, com foco em desenvolver experiência prática na construção de pipelines automatizados, integração entre sistemas, bancos de dados, containerização e orquestração de workflows.

```text
API → ETL → Airflow → Docker → MySQL
```

Da extração ao dado persistido. 🚀
