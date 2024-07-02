FROM python:3.12-alpine3.20

# Set the working directory to /app (or any directory you prefer)
WORKDIR /oxygen-cs

COPY requirements.txt requirements.txt
COPY src ./src

# Install necessary Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run your application
# Use the relative path from WORKDIR
ENTRYPOINT ["python3"]
CMD ["./src/main.py"]