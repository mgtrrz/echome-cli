scope := minor
main_branch_name := master

help: 
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: 		# Build sdist and bdist_wheel package files.
	python3 ./setup.py sdist bdist_wheel

clean: 		# Clean the contents of the 
	rm -rf build/ dist/ *.egg-info 

install:
	python3 setup.py install

publish:
	twine upload dist/*

.PHONY: help build clean install publish
.DEFAULT_GOAL := help
