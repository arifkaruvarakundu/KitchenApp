# Use a valid Python base image
FROM python:3.11-slim-bookworm

# Upgrade pip and system packages to ensure latest security patches
RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /Kitchen

# Install Python dependencies
COPY Kitchen/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 8000

# Run the Gunicorn server
# CMD ["gunicorn", "Kitchen.wsgi:application", "--bind", "0.0.0.0:8000"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]