.PHONY: all reformat tests

all: reformat

# todo: remove isort formating for autoflake and put all settings into pyproject.toml
reformat:
	isort --recursive --force-single-line botx tests
	autoflake --recursive --remove-all-unused-imports --remove-duplicate-keys --remove-unused-variables --in-place botx tests
	isort --recursive --multi-line=3 --trailing-comma --force-grid-wrap=0 --use-parentheses --line-width=88 botx tests
	black botx tests

lint: reformat
	flake8 botx
	mypy botx

	# todo: pylint - look at duplicated code later
	pylint \
		--disable=no-member \
		--disable=missing-docstring \
		--disable=bad-continuation \
		--disable=too-few-public-methods \
		--disable=too-many-arguments \
		--disable=duplicate-code \
		botx

tests:
	docker-compose up --build
