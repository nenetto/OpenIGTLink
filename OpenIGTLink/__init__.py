from __future__ import absolute_import, division, print_function, unicode_literals
import inspect as _inspect
import os as _os
import subprocess as _subprocess

_version_major = 1
_version_minor = 2
_version_patch = 0

try:
    _directory = _os.path.dirname(_os.path.dirname(_os.path.abspath(_inspect.getfile(_inspect.currentframe()))))

    _command = r'git rev-list --count HEAD'
    _version_patch = int(_subprocess.check_output(_command.split(), cwd=_directory).strip())

    _command = r'git rev-parse --short HEAD'
    __git__ = _subprocess.check_output(_command.split(), cwd=_directory).strip()

except (_subprocess.CalledProcessError, OSError):
    pass

__version__ = '{}.{}.{}'.format(_version_major, _version_minor, _version_patch)