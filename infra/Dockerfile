# Use the official Python image as a base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libmariadb-dev default-mysql-client

# Install Poetry
RUN pip install poetry

# Copy the Poetry configuration
COPY pyproject.toml poetry.lock /app/

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy the project files into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["/app/infra/entrypoint.sh"]