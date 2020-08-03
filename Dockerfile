FROM python:3.8.2

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3"]

# docker build -t tgbot .
# docker run --name tgbot-1 --restart always -p 10788:10788/udp -p 10789:10789/udp -v "PATH_FROM:/app" tgbot -u main.py
