#!/usr/bin/make -f

#venv:
#	. venv/bin/activate.fish

dev:
	export FLASK_APP=web_app; \
	export FLASK_ENV=development; \
	flask run

prod:
	export FLASK_APP=web_app; \
	export FLASK_ENV=production; \
	flask run

test:
	export FLASK_APP=web_app; \
	export FLASK_ENV=test; \
	flask run
