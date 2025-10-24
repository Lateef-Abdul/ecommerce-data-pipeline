.PHONY: help setup start stop clean pipeline analytics test

help:
	@echo "Available commands:"
	@echo "  make setup      - Install Python dependencies"
	@echo "  make start      - Start Docker containers"
	@echo "  make stop       - Stop Docker containers"
	@echo "  make data       - Generate sample data"
	@echo "  make pipeline   - Run complete ETL pipeline"
	@echo "  make analytics  - Run analytics queries"
	@echo "  make clean      - Clean data and restart"
	@echo "  make test       - Run tests"

setup:
	pip install -r requirements.txt

start:
	docker-compose up -d
	@echo "✓ Docker containers started"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  PgAdmin: http://localhost:5050"

stop:
	docker-compose down

data:
	python -m src.utils.generate_sample_data

pipeline:
	python -m src.run_pipeline

analytics:
	python -m src.utils.run_analytics

dashboard:
	streamlit run dashboards/ecommerce_dashboard.py

clean:
	docker-compose down -v
	rm -rf data/sample/*.csv
	@echo "✓ Cleaned all data"

test:
	pytest tests/ -v

restart: stop start
	@echo "✓ Containers restarted"

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-coverage:
	pytest --cov=src --cov-report=html tests/
	@echo "Coverage report: htmlcov/index.html"