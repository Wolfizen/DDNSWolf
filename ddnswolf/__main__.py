# Redirect top-level entrypoint to dedicated main module.
# This file supports the usage pattern of: `python -m ddnswolf`

from ddnswolf.main import main

main()
