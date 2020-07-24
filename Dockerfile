FROM python:3.8.2

WORKDIR /app

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "-u", "main.py"]