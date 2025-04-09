import cmdstanpy
print(cmdstanpy.__version__)  # Python package version

from cmdstanpy import cmdstan_path
print(cmdstan_path())  # Path to CmdStan installation