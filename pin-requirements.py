#!/usr/bin/env python3
"""
Re-pin requirements.txt, using pip-tools.

Given top-level depedencies, loosely specified, e.g. "this requires Flask >
1.0", recursively pin all dependencies and their dependencies to a particular
file using pip-tools.

Pip-tools requires this be done on version of Python that matches deployed
version, so we run this inside a container.

Licensed under MIT license; feel free to just check in to your repository.

> Need to package your Docker application for Docker?
> Read the [_Python on Docker Production Handbook_](https://pythonspeed.com/products/productionhandbook/)

Copyright (c) 2022 Hyphenated Enterprises LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import sys
import argparse
from tempfile import NamedTemporaryFile
from subprocess import check_output, CalledProcessError, check_call, STDOUT


SCRIPT = """\
set -e
python3 -m venv /tmp/venv3
. /tmp/venv3/bin/activate
pip install --upgrade pip pip-tools
pip-compile --generate-hashes "--output-file=$1" "$0"
"""


def main():
    """Run the program."""
    # Parse command-line arguments:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--image",
        help="Docker image to use for the build, e.g. 'python:3.9-slim'.",
        required=True,
    )
    parser.add_argument(
        "--in_file", help="High-level requirements file", default="requirements.in"
    )
    parser.add_argument(
        "--out_file",
        help="Pinned, transitive requirements file",
        default="requirements.txt",
    )

    args = parser.parse_args()

    # Ensure requirements.in exists:
    if not os.path.exists(args.in_file):
        raise SystemExit("Couldn't find file {}".format(args.in_file))

    # Determine if we need sudo for Docker, which is the case on Linux
    # typically:
    try:
        check_output(["docker", "version"], stderr=STDOUT)
        sudo_prefix = []
    except CalledProcessError:
        sudo_prefix = ["sudo"]

    # Make sure we can run docker now:
    check_output(sudo_prefix + ["docker", "version"])

    # We want uid/gid of requirements.txt to match the current uid/gid of
    # requirements.in:
    in_stat = os.stat(args.in_file)
    uid, gid = in_stat.st_uid, in_stat.st_gid

    # In Docker container with current directory mounted as volume, running as
    # appropriate uid and gid, create virtualenv, install pip-tools, run
    # pip-compile. We use pip-compile's --generate-hashes for extra security.
    out_file = NamedTemporaryFile(delete=False)
    out_file.close()
    check_call(
        sudo_prefix
        + [
            "docker",
            "run",
            "--user={}:{}".format(uid, gid),
            "--rm",
            "--env",
            "HOME=/tmp",
            "--mount",
            "type=bind,source={},target=/input".format(
                os.path.dirname(os.path.abspath(args.in_file))
            ),
            "--mount",
            "type=bind,source={},target=/output".format(
                os.path.dirname(os.path.abspath(args.out_file))
            ),
            "--entrypoint",
            "/bin/sh",
            args.image,
            "-c",
            SCRIPT,
            "/input/" + os.path.basename(args.in_file),
            "/output/" + os.path.basename(args.out_file),
        ]
    )

    # Write out final requirements.txt with correct instructions:
    with open(args.out_file) as f:
        lines = f.read().splitlines()
    with open(args.out_file, "w") as f:
        f.write("# Automatically generated from requirements.in using:\n")
        f.write("#   " + " ".join(sys.argv) + "\n")
        f.write("#\n")
        for line in lines:
            if not line.startswith("#"):
                f.write(line + "\n")


if __name__ == "__main__":
    main()
