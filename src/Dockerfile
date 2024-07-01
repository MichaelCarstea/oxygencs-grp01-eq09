FROM python:3.12-alpine3.16
WORKDIR main/src/main.py
COPY src ./src
RUN pip install --no-cache-dir -r HubConnectionBuilder -r load_dotenv

ENTRYPOINT ["python3"]
CMD ["./main.py"]