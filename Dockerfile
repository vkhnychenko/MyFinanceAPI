FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

EXPOSE 80

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt