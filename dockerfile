FROM python:3.10-slim-buster

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

# Command to run the FastAPI app
CMD ["python3", "app.py"]