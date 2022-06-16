# Resolve Secrets

Resolve Secret values from AWS Systems Manager or Secrets Manager.

This script was written to act as an entrypoint for Docker containers
requiring API Keys or other secrets from AWS Secrets Manager or
Systems manager parameter store. Should not be needed in cases were
the injection is provided by AWS, but was required in the past for
some specific scenarios.

The variables are printed into stdout in the export=... format so that
the can be sourced by the parent process.
## Usage

Install dependencies (create virtualenv if needed before):

```sh
pip3 install -r requirements.txt
```

Define the env variables to be resolved, typically these are configured in
CF or other IaC templates:

```sh
export API_KEY="[resolve:ssm-secure]/project/env/API_KEY"
export OTHER_SECRET="[resolve:secretsmanager]/project/env/OtherSecret"
```

Run the script:

```sh
python3 resolve-secrets.py API_KEY OTHER_SECRET --raise-exceptions
```

Assuming the parameter exists (in SSM in this case) and can be successfully retrieved,
the program will print the retrieved variables in the console, e.g.:

```sh
export API_KEY=RESOLVED_SECRET1
export OTHER_SECRET=RESOLVED_SECRET2
```
The retrieved variables can be sourced by

```sh
source $(python3 resolve-secrets.py)
```

## Contributing

The file is linted using Pep8 standard:

```sh
pip3 install pylint
pylint resolve_secrets.py
```

The typing is checked with mypy:

```sh
pip3 install mypy
mypy resolve_secrets.py
```