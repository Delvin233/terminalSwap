.PHONY: test lint format install setup-hooks

# Install dependencies
install:
	pip install -r requirements.txt

# Setup pre-commit hooks
setup-hooks:
	pre-commit install

# Run tests
test:
	pytest

# Run linting
lint:
	flake8 src/ tests/

# Format code
format:
	black src/ tests/

# Run all checks (like pre-commit)
check: format lint test
	@echo "✅ All checks passed!"

# Setup everything
setup: install setup-hooks
	@echo "🚀 Setup complete! Ready to develop."