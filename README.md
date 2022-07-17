# DDNSWolf

See `LICENSE.md` for your license to use this software.


## Using DDNSWolf

WIP

## Modifying DDNSWolf

### Building for development

Create a virtual environment, if desired.

    python3 -m virtualenv ./venv
    . ./venv/bin/activate

Install dependencies. There is no `requirements.txt` file, instead
dependencies are declared in `setup.cfg` and pip can read this file.

    pip install .

### Building for distribution

This project uses Python `setuptools` to build for distribution.
The build configuration is defined in `setup.cfg` and `setup.py`.

To install the package on your system:

    python3 setup.py
