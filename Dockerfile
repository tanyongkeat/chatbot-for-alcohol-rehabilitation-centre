FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN python3 -c "from sentence_transformers import SentenceTransformer; import gc; model = SentenceTransformer('paraphrase-xlm-r-multilingual-v1'); del model; gc.collect()"
