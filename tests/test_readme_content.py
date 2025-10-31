from pathlib import Path


def test_readme_contains_required_sections_and_commands():
    readme_path = Path("README.md")
    assert readme_path.exists(), "README.md must exist"
    text = readme_path.read_text(encoding="utf-8")

    # Required headers
    required_headers = [
        "Getting Started",
        "Installation",
        "Running the Application",
        "Running Tests",
        "Docker Deployment",
    ]
    for header in required_headers:
        assert header in text, f"Missing README section: {header}"

    # Required commands/strings
    required_commands = [
        "poetry install",
        "poetry run streamlit run app.py",
        "make run",
        "poetry run pytest",
        "make test",
        "make build-image",
        "make run-image",
        "Streamlit Calculator Web App",
    ]
    for cmd in required_commands:
        assert cmd in text, f"Missing README command or string: {cmd}"
