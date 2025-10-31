FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Avoid caching pip packages
ENV PIP_NO_CACHE_DIR=1

# Install build dependencies for some python packages if necessary
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir "poetry>=1.1.13"

# Copy poetry files first for layer caching (poetry.lock may not exist)
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry to install into the system environment and install deps
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev

# Copy application source
COPY . /app

# Expose Streamlit default port
EXPOSE 8501

# Run the Streamlit app
CMD ["poetry", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
