help:
	@echo Try \`make init, fetch, or repl\`

init:
	virtualenv venv
	./venv/bin/pip install requests
	./venv/bin/pip install pyquery

fetch:
	./venv/bin/python fetch_errors.py

repl:
	./venv/bin/python