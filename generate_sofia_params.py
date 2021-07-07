#!/usr/bin/env python3

import os
import sys
import argparse
import configparser
from jinja2 import Template


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input file for mosaicked image cube.",
    )
    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        required=True,
        help="Sofia parameters filename",
    )
    parser.add_argument(
        "-t",
        "--template",
        type=str,
        required=False,
        help="SoFiA parameter file template",
        default="/app/templates/sofia.j2"
    )
    parser.add_argument(
        "-d",
        "--defaults",
        type=str,
        required=False,
        help="SoFiA parameter file default values",
        default="/app/templates/sofia.ini"
    )
    args = parser.parse_args(argv)
    return args


def read_defaults(f):
    """Read default values from a config parser.

    """
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(f)
    return dict(config.items("DEFAULT"))


def read_environ():
    """Read parameter inputs from environment variables

    """
    env = {}
    keys = [k for k in list(os.environ) if "SOFIA" in k]
    for k in keys:
        env[k] = os.environ[k]
    return env


def main(argv):
    """Create a SoFiA parameter file from Nextflow parameters.
    Default values provided in templates/sofia.ini file.
    Parameter values are passed as keyword arguments.

    """
    # Get arguments
    args = parse_args(argv)
    data = {
        'SOFIA_INPUT_DATA': args.input,
    }

    # Get sofia parameter file template
    with open(args.template, 'r') as f:
        template = Template(f.read())

    # Get default values
    defaults = read_defaults(args.defaults)
    defaults['SOFIA_OUTPUT_DIRECTORY'] = args.filename.rsplit('/', 1)[0]

    env = read_environ()

    # Update template with parameters
    if env is not None:
        params = {**defaults, **env}
        params = {**params, **data}
    else:
        params = {**defaults, **data}
    config = template.render(params)

    # Write parameter file
    with open(args.filename, 'w') as f:
        f.writelines(config)
    print(args.filename, end="")


if __name__ == "__main__":
    main(sys.argv[1:])