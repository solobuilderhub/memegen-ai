## Commands

pip install fastapi[standard] - For running fastapi command from cml.
pip freeze | Out-File -FilePath requirements.txt -Encoding utf8

e.g.: fastapi dev app/main.py

Prod: uvicorn app.main:app --host 0.0.0.0 --port 8000

## Faster processing in prod with uvloop event:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop uvloop --http httptools

we can also add multiple worker(threads) for more cpu usage by setting worker parmeter in uvicorn.

### Resources:

pip install --upgrade setuptools

setuptools is a library that facilitates the packaging and distribution of Python projects. It extends Python’s distutils to provide more powerful and flexible options for defining package metadata, dependencies, entry points, and more.

setup.py is a build script for Python projects. It uses setuptools (a collection of enhancements to the Python distutils that allow you to more easily build and distribute Python packages, especially ones that have dependencies on other packages) to describe your project and its dependencies. This file is essential for:

Packaging Your Project: Allows others to install your project using pip.
Managing Dependencies: Specifies which packages your project depends on.
Enabling Development Mode: Facilitates installing your project in editable mode (pip install -e .), making development easier.

Defining Your Package: Ensures Python recognizes your project as a package, making imports straightforward.
Managing Dependencies: Lists all the required packages so that they are installed when setting up your project.
Facilitating Script Execution: Allows your scripts to access project modules without manipulating sys.path manually

## Extra

b. Installing Your Package in Development Mode
To make your project easily accessible within your venv and to ensure that changes to your code are immediately reflected without reinstalling, you should install your package in editable or development mode.

From your project's root directory (where setup.py is located), run:

pip install -e .

#sample api_key can be generated with open ssl e.g.:
671e5e626f0af498e29c36e2.y7XjvzldmzWU8r0EfaKteAfeUzLwml6l
