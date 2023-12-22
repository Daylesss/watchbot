FROM python:3.9

RUN mkdir /bot

WORKDIR /bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x app.sh
# RUN alembic upgrade head

# CMD ["python", "main.py"]