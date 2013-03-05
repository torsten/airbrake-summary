help:
	@echo Try \`make help, init, fetch, cluster, or repl\`

init:
	virtualenv venv
	./venv/bin/pip install requests
	./venv/bin/pip install pyquery
	./venv/bin/pip install sh

init3:
	virtualenv venv3 -p python3.3
	./venv3/bin/pip-3.3 install -i http://simple.crate.io/ requests
	./venv3/bin/pip-3.3 install -i http://simple.crate.io/ pyquery
	./venv3/bin/pip-3.3 install -i http://simple.crate.io/ sh

fetch:
	./venv/bin/python fetch_errors.py

cluster:
	./venv/bin/python cluster_duplicates.py

repl:
	./venv/bin/python
