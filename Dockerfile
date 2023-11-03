FROM python:3.11.5
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN apt update; apt install -y libgl1
# CMD ["flask", "run", "--host", "0.0.0.0"]
CMD ["gunicorn", "--bind", "--host", "0.0.0.0:80", "app:create_app()"]