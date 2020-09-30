#!/usr/bin/env python3
"""
runeq command line interface

"""
import os
import yaml

import click

from runeq.config import DEFAULT_CONFIG_YAML


def _write_config(values):
    """
    Write values to the configuration file. Overwrites any existing content.

    """
    filepath = os.path.expanduser(DEFAULT_CONFIG_YAML)

    # Create the directory if it doesn't exist
    dirpath = os.path.dirname(filepath)
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)

    with open(filepath, 'w') as f:
        yaml.dump(values, f)


def _get_config() -> dict:
    """
    Get or create the config file

    """
    filepath = os.path.expanduser(DEFAULT_CONFIG_YAML)
    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath) as f:
            values = yaml.safe_load(f)

        valid = isinstance(values, dict) or not values
    except yaml.YAMLError:
        valid = False

    if valid:
        return values or {}

    # If the contents of the config file are not a dictionary, ask the user
    # if they want to overwrite the contents.
    prompt = (
        'Detected invalid contents in the config file ({})\nWould you like to '
        'reset the contents?'.format(filepath)
    )
    if not click.confirm(click.style(prompt, fg='red')):
        raise click.Abort()

    _write_config({})
    return {}


@click.group()
def cli():
    """
    runeq command line interface

    """


@cli.group()
def configure():
    """
    Manage runeq configuration (stored in a YAML file).

    """


@configure.command()
@click.option('--access-token-id', required=True,
              prompt='Enter an access token ID',
              help='Rune access token ID')
@click.option('--access-token-secret', required=True,
              prompt='Enter an access token secret',
              help='Rune access token secret')
def setup(access_token_id, access_token_secret):
    """
    Set up a runeq configuration file. This will overwrite any existing values.

    """
    if _get_config():
        prompt = (
            'Found existing config values. Would you like to overwrite them?'
        )
        if not click.confirm(click.style(prompt, fg='red')):
            raise click.Abort()

    _write_config({
        'access_token_id': access_token_id,
        'access_token_secret': access_token_secret,
    })
    click.echo(click.style(
        f'Success! Created a configuration file: {DEFAULT_CONFIG_YAML}',
        fg='green'
    ))


@configure.command()
@click.option('--key', '-k', default='', multiple=True, required=False,
              help='1+ keys to fetch')
def get(key):
    """
    Print one or more values from the current runeq configuration. If no keys
    are specified, prints all existing values.

    """
    config = _get_config()

    if not key:
        for k in sorted(config):
            print('{}: {}'.format(k, config[k]))
    else:
        for k in key:
            print('{}: {}'.format(k, config.get(k, '')))


@configure.command()
@click.option('--value', '-v', multiple=True, required=True,
              help='1+ values to set in the config file. Each option should'
                   'be provided as [key]=[value]')
def set(value):
    """
    Set a value in the runeq configuration file.

    """
    config = _get_config()

    for item in value:
        elements = item.split('=')
        if len(elements) != 2:
            raise click.ClickException(
                'Each option must be provided as [key]=[value]'
            )

        k, v = elements
        config[k.strip()] = v.strip()

    _write_config(config)


if __name__ == '__main__':
    cli()
