FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y libpq-dev gcc && pip3 install -r requirements.txt

RUN python3 -c "from sentence_transformers import SentenceTransformer; import gc; model = SentenceTransformer('paraphrase-xlm-r-multilingual-v1'); del model; gc.collect()"

# RUN apt-get install -y g++ && pip3 install plotly youtokentome malaya
RUN apt-get install -y g++ && pip3 install plotly

COPY . /app

EXPOSE 5000

# CMD python chatbot.py

# docker run -p 5000:5000 -v ${pwd}:/app fyp_app:first