#!/usr/bin/env python3

import argparse
import os
import boto3
import logging

logger = logging.getLogger('secrets')

SSM_PREFIX = '[resolve:ssm-secure]'
SM_PREFIX = '[resolve:secretsmanager]'

def parse_args():
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('variables', type=str, nargs='+')
	parser.add_argument('--raise-exceptions', action='store_true', default=False)
	args = parser.parse_args()
	return args

def should_resolve(secret_str):
	if secret_str.startswith(SSM_PREFIX) or secret_str.startswith(SM_PREFIX):
		return True
	else:
		return False

def get_ssm_secret(secret_id, raise_exception):
	logger.info('Retrieving SSM secret')

	client = boto3.client('ssm')
	try:
		secret_value = client.get_parameter(Name=secret_id, WithDecryption=True)
		return secret_value['Parameter']['Value']
	except client.exceptions.ResourceNotFoundException as e:
		if raise_exception:
			raise e

def get_sm_secret(secret_id, raise_exception):
	logger.info('Retrieving Secretsmanager secret')
	client = boto3.client('secretsmanager')
	try:
		secret_value = client.get_secret_value(SecretId=secret_id)
		return secret_value['SecretString']
	except client.exceptions.ResourceNotFoundException as e:
		if raise_exception:
			raise e

def resolve(secret_str, raise_exception):
	"""Validate that the value is actually a secret."""
	if secret_str.startswith(SSM_PREFIX):
		secret_id = secret_str[len(SSM_PREFIX):]
		return get_ssm_secret(secret_id, raise_exception)

	elif secret_str.startswith(SM_PREFIX):
		secret_id = secret_str[len(SM_PREFIX):]
		return get_sm_secret(secret_id, raise_exception)

def main(secrets_to_parse, raise_exception):
	for secret_key in secrets_to_parse:
		secret_str = os.environ.get(secret_key)
		if secret_str is not None and should_resolve(secret_str):

			secret_value = resolve(secret_str, raise_exception)
			if secret_value is not None:
				print('export %s=%s' % (secret_key, secret_value))

if __name__ == '__main__':
	args = parse_args()
	logger.info(args)
	main(args.variables, args.raise_exceptions)

#logger.info('export TMP_VARIABLE=123')