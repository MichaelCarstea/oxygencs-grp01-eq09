FROM python:3.12-alpine3.20
# Set the working directory to /app (or any directory you prefer)
WORKDIR /oxygencs-grp01-eq09

# If you need everything from your project, this single COPY is enough.
# If you only need specific directories or files, adjust the COPY commands accordingly.
COPY . .

# Install necessary Python packages
RUN pip install --no-cache-dir requests signalrcore python-dotenv

# Set the command to run your application
# Use the relative path from WORKDIR
ENTRYPOINT ["python3"]
CMD ["src/main.py"]