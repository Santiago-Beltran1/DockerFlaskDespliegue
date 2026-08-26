FROM python:3.10-slim

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /home/myapp

COPY requirements.txt .

RUN pip install --upgrade pip setuptools>=78.1.1 msgpack>=1.2.1 && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5050
CMD ["python3", "sample_app.py"]