# Streamlit Calculator Web App

## Description

Streamlit Calculator Web App is a lightweight Streamlit application that provides high-precision arithmetic operations and a simple, session-persistent calculation history. It is built with Python and managed with Poetry for dependency and environment handling. This README explains how to set up, run, test, and deploy the application.

## Getting Started

These instructions will get a copy of the project running on your local machine for development and testing purposes.

Prerequisites

- Python 3.9+ (Python 3.11 recommended)
- Poetry (for dependency and virtualenv management)
- Docker (optional, for containerized deployment)
- Make (optional, for convenience targets provided in Makefile)

## Installation

1. Clone the repository:

   git clone <repository-url>
   cd <repository-directory>

2. Install Python dependencies using Poetry:

   poetry install

3. Create a development .env file if needed (optional):

   cp .env.example .env
   # Edit .env as required

Note: The project uses a Config class pattern (e.g., src/gsp_calculator/config.py) to centralize environment configuration.

## Running the Application

Run locally with Streamlit (development):

poetry run streamlit run app.py

Alternatively, use the provided Makefile convenience target:

make run

The app will be available at http://localhost:8501 by default.

## Running Tests

Run the test suite locally with pytest:

poetry run pytest

Or use the Makefile convenience target:

make test

Tests verify project components and documentation consistency.

## Docker Deployment

Build a Docker image using the Makefile or Docker directly.

Using Makefile:

make build-image
make run-image

Commands explained:

- make build-image: builds a Docker image named calculator-web-streamlit
- make run-image: runs the built image and exposes port 8501 to host

Direct Docker commands:

# Build
docker build -t calculator-web-streamlit .

# Run
docker run -p 8501:8501 calculator-web-streamlit

## Environment and Configuration

- Store runtime configuration in a .env file at the repository root for development.
- Use src/gsp_calculator/config.py (or similar) to read environment variables.
- Never commit sensitive credentials to the repository.

## Troubleshooting

- If Streamlit fails to start, check for conflicting processes on port 8501.
- If dependencies fail to install, ensure Poetry and Python versions match the prerequisites.

## Project Structure (overview)

- app.py - Streamlit application entrypoint
- src/gsp_calculator/ - package for calculator logic and config
- tests/ - pytest test suite
- Makefile - helpful targets for install, run, test, build-image, run-image
- Dockerfile - container definition for deployment

## Contributing

Contributions are welcome. Please follow repository contribution guidelines and ensure tests pass before submitting PRs.

## License

Specify license information here if applicable.
