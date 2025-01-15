bump:
	@echo "Bumping ai-experiments version"
	@poetry version patch
	@echo "Bumped ai-experiments version"

pre-bump:
	@echo "Bumping Version to Pre-release"
	@poetry version prerelease
	@echo "Bumped Version to Pre-release"

publish:
	@echo "Publishing ai-experiments to PyPi"
	@rm -rf dist
	@poetry build
	@poetry publish
	@echo "Published ai-experiments to PyPi"

fmt:
	@echo "Formatting ai-experiments code"
	@poetry run python -m ruff format
	@echo "Formatted ai-experiments code"

fix:
	@echo "Checking ai-experiments code"
	@poetry run python -m ruff check --fix
	@echo "Checked ai-experiments code"

test:
	@echo "Running ai-experiments tests"
	@poetry run python -m tests.main

cli:
	@echo "play cli blackjack"
	@poetry run python -m apps.blackjack.functions.main

blackjack:
	@echo "play blackjack"
	@poetry run python -m apps.blackjack.main

customer_service:
	@echo "play customer_service"
	@poetry run python -m apps.customer_service.main

.PHONY: bump pre-bump publish fmt fix test cli blackjack customer_service
