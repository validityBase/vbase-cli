import click
from enum import Enum
import json
import os


# Define vBase OperationType as an Enum.
class OperationType(Enum):
    # A commit operation is a write (execute) operation that records data
    # and changes the state of the commitment service.
    COMMIT = "commit"
    # A verify operation is a read operation that validates data
    # and does not change the state of the commitment service.
    VERIFY = "verify"


# Define the path to the configuration file.
# The configuration file is used to store persistent configuration settings.
# These can be overridden by environment variables and command-line optios.
CONFIG_FILE_PATH = os.path.join(
    os.path.expanduser("~"), ".config", "vbase", "config.json"
)


def load_config():
    """
    Load configuration from file and environment variables.

    Configuration is handled as follows:
    - Environment Variables: Allow configuration via environment variables for flexibility
      and ease of use in different environments (e.g., CI/CD).
    - Configuration Files: Provide support for storing persistent configuration in a file
      (e.g., in ~/.config/vbase/), ensuring settings can be reused across sessions without needing to set them every time.
    - Command-Line Flags: Provide command-line flags for immediate overrides.
    - Precedence: Command-line flags take precedence over environment variables,
      environment variables should take precedence over values in configuration files.
    """
    config = {}
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as f:
            config = json.load(f)

    for var_name in [
        "VBASE_COMMITMENT_SERVICE_NODE_RPC_URL",
        "VBASE_COMMITMENT_SERVICE_ADDRESS",
        "VBASE_COMMITMENT_SERVICE_PRIVATE_KEY",
        "VBASE_FORWARDER_URL",
        "VBASE_API_KEY",
    ]:
        config[var_name] = os.getenv(var_name, config.get(var_name))

    return config


def validate_commit_operation(
    vb_cs_node_rpc_url, vb_cs_address, vb_cs_private_key, vb_forwarder_url, vb_api_key
):
    """Validate the options for a commit (write) operation."""
    # Direct node access: [--vb_cs_node_rpc_url, --vb_cs_address, --vb_cs_private_key]
    if vb_cs_node_rpc_url and vb_cs_address and vb_cs_private_key:
        return
    # Forwarder access: [--vb_forwarder_url, --vb_api_key] with an optional --vb_cs_private_key
    elif vb_forwarder_url and vb_api_key:
        return
    # Otherwise, invalid combination
    raise click.UsageError(
        "For a commit (write) operation, you must specify either [--vb_cs_node_rpc_url, --vb_cs_address, --vb_cs_private_key] "
        "or [--vb_forwarder_url, --vb_api_key] with an optional --vb_cs_private_key."
    )


def validate_verify_operation(
    vb_cs_node_rpc_url, vb_cs_address, vb_forwarder_url, vb_api_key
):
    """Validate the options for a verify (read) operation."""
    # Direct node access: [--vb_cs_node_rpc_url, --vb_cs_address]
    if vb_cs_node_rpc_url and vb_cs_address:
        return
    # Forwarder access: [--vb_forwarder_url, --vb_api_key]
    elif vb_forwarder_url and vb_api_key:
        return
    # Otherwise, invalid combination
    raise click.UsageError(
        "For a verify (read) operation, you must specify either [--vb_cs_node_rpc_url, --vb_cs_address] "
        "or [--vb_forwarder_url, --vb_api_key]."
    )


def global_options(operation_type: OperationType):
    """Decorator to add global configuration options and validate inputs based on operation type."""

    def wrapper(f):
        @click.option(
            "--vb_cs_node_rpc_url", help="vBase commitment service node RPC URL"
        )
        @click.option(
            "--vb_cs_address", help="vBase commitment service smart contract address"
        )
        @click.option(
            "--vb_cs_private_key", help="vBase commitment service private key"
        )
        @click.option("--vb_forwarder_url", help="vBase forwarder URL")
        @click.option("--vb_api_key", help="vBase API key")
        @click.pass_context
        def new_func(
            ctx,
            vb_cs_node_rpc_url,
            vb_cs_address,
            vb_cs_private_key,
            vb_forwarder_url,
            vb_api_key,
            *args,
            **kwargs
        ):
            ctx.ensure_object(dict)
            for key, value in kwargs.items():
                if value:
                    ctx.obj[key] = value

            # Validate the configuration based on the operation type
            if operation_type == OperationType.COMMIT:
                validate_commit_operation(
                    vb_cs_node_rpc_url,
                    vb_cs_address,
                    vb_cs_private_key,
                    vb_forwarder_url,
                    vb_api_key,
                )
            elif operation_type == OperationType.VERIFY:
                validate_verify_operation(
                    vb_cs_node_rpc_url, vb_cs_address, vb_forwarder_url, vb_api_key
                )

            return f(ctx, *args, **kwargs)

        return click.decorators.update_wrapper(new_func, f)

    return wrapper
