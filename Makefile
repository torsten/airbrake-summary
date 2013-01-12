help:
	@echo Try \`make help, init, fetch, cluster, or repl\`

init:
	virtualenv venv
	./venv/bin/pip install requests
	./venv/bin/pip install pyquery
	./venv/bin/pip install sh

fetch:
	./venv/bin/python fetch_errors.py

cluster:
	./venv/bin/python cluster_duplicates.py

repl:
	./venv/bin/python
