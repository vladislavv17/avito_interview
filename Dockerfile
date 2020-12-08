FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./requirements.txt /code/requirements.txt

WORKDIR /code/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /code/

EXPOSE 8000