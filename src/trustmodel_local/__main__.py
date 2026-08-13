"""Enable `python -m trustmodel ...` as a PATH-independent fallback for the CLI.

If the `trustmodel` console script isn't on your PATH (common with
`pip install --user`), you can always invoke the same CLI via the module form:

    python -m trustmodel login
    python -m trustmodel eval "some AI output"
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
