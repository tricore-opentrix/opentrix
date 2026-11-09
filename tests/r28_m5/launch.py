#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 TRICORE contributors
# SPDX-License-Identifier: Apache-2.0
"""Start M5 in a new process with an explicit OS-only environment."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

OS_ENV = ('PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'PATHEXT', 'COMSPEC')


def main():
    env = {k: v for k, v in os.environ.items() if k.upper() in OS_ENV}
    with tempfile.TemporaryDirectory(prefix='r28-m5-home-') as home:
        env.update(HOME=home, USERPROFILE=home)
        return subprocess.run([sys.executable, '-I', '-B', str(Path(__file__).with_name('run.py')),
                               *sys.argv[1:]], env=env).returncode


if __name__ == '__main__':
    sys.exit(main())
