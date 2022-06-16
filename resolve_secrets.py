#!/usr/bin/env python3
"""Resolve Secret values from AWS Systems Manager or Secrets Manager.

This script was written to act as an entrypoint for Docker containers
requiring API Keys or other secrets from AWS Secrets Manager or
Systems manager parameter store. Should not be needed in cases were
the injection is provided by AWS, but was required in the past for
some specific scenarios.

The variables are printed into stdout in the export VARIABLE=... format so that
the can be sourced by the parent process.
"""
import argparse
import os
import logging
from typing import List, Optional

import boto3

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('SecretResolver')

# Prefixes for the secrets. Will be used to identify the values intended
# to be resolved
SSM_PREFIX = '[resolve:ssm-secure]'
SM_PREFIX = '[resolve:secretsmanager]'

ssm_client = boto3.client('ssm')
sm_client = boto3.client('secretsmanager')


def parse_args():
    """Parse commandline arguments"""
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('variables', type=str, nargs='+')
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument(
        '--raise-exceptions',
        action='store_true',
        default=False)
    parsed_args = parser.parse_args()
    return parsed_args


def should_resolve(secret_str: Optional[str]) -> bool:
    """Check if given variable name should be resolved"""
    if secret_str is not None and (secret_str.startswith(
            SSM_PREFIX) or secret_str.startswith(SM_PREFIX)):
        return True

    return False


def get_ssm_secret(secret_id: str, raise_exception: bool) -> Optional[str]:
    """Resolve secret from System Manager Parameter store"""
    logger.debug('Retrieving SSM secret')
    try:
        secret_value = ssm_client.get_parameter(
            Name=secret_id, WithDecryption=True)
        return secret_value['Parameter']['Value']
    except ssm_client.exceptions.ResourceNotFoundException as ex:
        if raise_exception:
            raise ex

        return None


def get_sm_secret(secret_id: str, raise_exception: bool) -> Optional[str]:
    """Resolve secret from Secrets Manager"""
    logger.debug('Retrieving Secretsmanager secret')

    try:
        secret_value = sm_client.get_secret_value(SecretId=secret_id)
        return secret_value['SecretString']
    except sm_client.exceptions.ResourceNotFoundException as ex:
        if raise_exception:
            raise ex

        return None


def resolve_secret(secret_str: str, raise_exception: bool) -> Optional[str]:
    """Validate that the value is actually a secret."""

    print(secret_str)
    if secret_str.startswith(SSM_PREFIX):
        secret_id = secret_str[len(SSM_PREFIX):]
        return get_ssm_secret(secret_id, raise_exception)

    if secret_str.startswith(SM_PREFIX):
        secret_id = secret_str[len(SM_PREFIX):]
        return get_sm_secret(secret_id, raise_exception)

    return None


def main(secrets_to_parse: List[str], raise_exception: bool):
    """Resolve a specified list of secrets from SSM or SM and print in export format"""
    for secret_key in secrets_to_parse:
        secret_str = os.environ.get(secret_key)
        if should_resolve(secret_str):
            resolved_secret = resolve_secret(secret_str, raise_exception)
            if resolved_secret is not None:
                print(f'export {secret_key}={resolved_secret}')


if __name__ == '__main__':
    args = parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.debug(args)
    main(args.variables, args.raise_exceptions)
