scope := minor
main_branch_name := master

.PHONY: help
help: 
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: 		# Build sdist and bdist_wheel package files.
	python3 ./setup.py sdist bdist_wheel

.PHONY: clean
clean: 		# Clean the contents of the 
	rm -rf build/ dist/ *.egg-info 

.PHONY: publish
publish:
	twine upload dist/*

.DEFAULT_GOAL := help
