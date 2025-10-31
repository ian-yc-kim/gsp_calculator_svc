.PHONY: install-deps run test build-image run-image

install-deps:
	poetry install

run:
	poetry run streamlit run app.py

test:
	poetry run pytest

build-image:
	docker build -t calculator-web-streamlit .

run-image:
	docker run -p 8501:8501 calculator-web-streamlit
