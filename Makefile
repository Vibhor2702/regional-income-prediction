.PHONY: help install prepare train interpret dashboard test clean docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install all dependencies"
	@echo "  make prepare       - Download and prepare data"
	@echo "  make train         - Train machine learning models"
	@echo "  make interpret     - Generate model interpretation reports"
	@echo "  make dashboard     - Run Streamlit dashboard locally"
	@echo "  make test          - Run unit tests"
	@echo "  make clean         - Clean generated files"
	@echo "  make docker-build  - Build Docker container"
	@echo "  make docker-run    - Run Docker container"

# Install dependencies
install:
	pip install -r requirements.txt

# Download and prepare data
prepare:
	python src/data_ingest.py

# Train models
train:
	python src/modeling.py

# Generate interpretations
interpret:
	python src/interpret.py

# Run dashboard
dashboard:
	streamlit run app/streamlit_app.py

# Run tests
test:
	pytest tests/ -v --cov=src --cov-report=html

# Clean generated files
clean:
	rm -rf data_raw/* data_processed/* models/* reports/feature_importance/*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build Docker image
docker-build:
	docker build -t regional-income-prediction:latest .

# Run Docker container
docker-run:
	docker run -p 8501:8501 -v $(PWD)/data_processed:/app/data_processed -v $(PWD)/models:/app/models regional-income-prediction:latest
