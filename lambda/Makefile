# In your python env, run `make install` to insall required packages
# and then either `make` for a single test run
# or `make watch` for a continuous pipeline that reruns on changes.
#
# Comments to cyber.security@digital.cabinet-office.gov.uk
# This is free and unencumbered software released into the public domain.

.SILENT: test install upgrade watch checks target_dir add_deps copy_dir build run zip

clean:
	rm -rf __pycache__ .coverage *.zip *.egg-info .tox venv .pytest_cache htmlcov **/__pycache__ **/*.pyc .target setup.cfg
	echo "✔️ Cleanup of files completed!"

test: checks
	pytest -sqx --disable-warnings
	echo "✔️ Tests passed!"

checks: clean
	echo "⏳ running pipeline..."
	set -e
	echo "isorting"
	isort --atomic -q .
	echo "blacking"
	black -q .
	echo "flake8ing"
	flake8 . --max-line-length=91
	echo "mypying"
	mypy --warn-unused-config \
             --disallow-any-generics \
             --disallow-subclassing-any \
             --disallow-untyped-calls \
             --disallow-untyped-defs \
             --disallow-incomplete-defs \
             --check-untyped-defs \
             --no-implicit-optional \
             --warn-redundant-casts \
             --warn-unused-ignores \
             --warn-return-any \
             --no-implicit-reexport \
             --strict-equality .
	echo "✔️ Checks pipeline passed!"

install:
	set -e
	echo "⏳ installing..."
	pip -q install black flake8 mypy watchdog pyyaml argh pytest isort
	mypy_boto3 -q && echo  "✔️ mypy_boto3 stubs installed!"!! || true # ignored if not installed
	pip install -r requirements-dev.txt
	echo "✔️ Pip dependencies installed!"

watch:
	echo "✔️ Watch setup, save a python file to trigger test pipeline"
	watchmedo shell-command --drop --ignore-directories --patterns="*.py" --ignore-patterns="*#*" --recursive --command='clear && make --no-print-directory test' .

target_dir:
	rm -rf .target/
	mkdir .target

add_deps: target_dir
	bash -c "echo -e '[install]\nprefix=\n' > setup.cfg"; python3 -m pip install -r requirements.txt -t .target

copy_dir:
	cp *.py .target/

build: clean target_dir add_deps copy_dir

run:
	python3 run.py

zip: build
	cd .target; zip -X -9 ../github_usage_lambda.zip -r .
	echo "✔️ zip file built!"
