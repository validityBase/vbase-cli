"""Configuration module for vBase CLI."""

import json
import os
import click


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
      (e.g., in ~/.config/vbase/), ensuring settings can be reused across sessions
      without needing to set them every time.
    - Command-Line Flags: Provide command-line flags for immediate overrides.
    - Precedence: Command-line flags take precedence over environment variables,
      environment variables should take precedence over values in configuration files.
    """
    config = {}
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
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
    # Direct node access: [--vb-cs-node-rpc-url, --vb-cs-address, --vb-cs-private-key]
    if vb_cs_node_rpc_url and vb_cs_address and vb_cs_private_key:
        return
    # Forwarder access: [--vb-forwarder-url, --vb-api-key] with an optional --vb-cs-private-key
    if vb_forwarder_url and vb_api_key:
        return
    # Otherwise, invalid combination
    raise click.UsageError(
        "For a commit (write) operation, you must specify either "
        "[--vb-cs-node-rpc-url, --vb-cs-address, --vb-cs-private-key] "
        "or [--vb-forwarder-url, --vb-api-key] with an optional --vb-cs-private-key."
    )


def validate_verify_operation(
    vb_cs_node_rpc_url, vb_cs_address, vb_forwarder_url, vb_api_key
):
    """Validate the options for a verify (read) operation."""
    # Direct node access: [--vb-cs-node-rpc-url, --vb-cs-address]
    if vb_cs_node_rpc_url and vb_cs_address:
        return
    # Forwarder access: [--vb-forwarder-url, --vb-api-key]
    if vb_forwarder_url and vb_api_key:
        return
    # Otherwise, invalid combination
    raise click.UsageError(
        "For a verify (read) operation, you must specify either "
        "[--vb-cs-node-rpc-url, --vb-cs-address] "
        "or [--vb-forwarder-url, --vb-api-key]."
    )
