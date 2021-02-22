#!/usr/bin/env python

# PEP 396 -- Module Version Numbers
# https://www.python.org/dev/peps/pep-0396/
# PEP 440 - Version Identification and Dependency Specification
# https://www.python.org/dev/peps/pep-0440/

_verMaj = 0  # breaking change
_verMin = 0  # non-breaking change
__version__ = ".".join([str(_verMaj), str(_verMin)])
