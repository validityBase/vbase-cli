#!/usr/bin/python3

"""vBase CLI for object commitment and verification"""

from functools import wraps
import logging
import pprint
import re
import click
import cloup

from vbase import (
    VBaseClient,
    Web3HTTPCommitmentService,
    ForwarderCommitmentService,
)

from vbasecli.config import load_config


def is_valid_cid(s):
    # Regular expression to match a valid CID.
    # A CID is a 256-byte (64-hex digit) string in hex representation.
    # It must start with '0x' and be followed by 64 hexadecimal characters.
    pattern = r"^0x[0-9a-fA-F]{64}$"
    return re.match(pattern, s)


def needs_object_cid_options(f):
    """Decorator to add shared input options for commands that require an object_cid."""

    @wraps(f)
    @cloup.option("--object-cid", help="Specify object CID")
    @cloup.option("--object-cid-stdin", is_flag=True, help="Read object CID from stdin")
    def wrapper(ctx, *args, **kwargs):
        return ctx.invoke(f, ctx, *args, **kwargs)

    return wrapper


def get_object_cid(object_cid, object_cid_stdin):
    """Helper function to get object_cid from argument or stdin."""
    # Handle object_cid and object_cid-stdin.
    object_cid_value = ""
    if object_cid:
        object_cid_value = object_cid
    elif object_cid_stdin:
        object_cid_value = click.get_text_stream("stdin").read()
    else:
        raise click.UsageError(
            "You must specify either --object-cid or --object-cid-stdin."
        )

    if not object_cid_value:
        raise click.UsageError("Undefined object CID value.")

    # Strip leading and trailing whitespace to make sure the CID is clean
    # and hex string -> bytes conversion works correctly.
    object_cid_value = object_cid_value.strip()

    if not is_valid_cid(object_cid_value):
        raise click.UsageError(
            "Invalid object CID value. Please specify a valid 256-bit hex string."
        )

    return object_cid_value


def setup_logging(verbosity):
    """Set up logging based on the verbosity level."""
    log_level = logging.WARNING

    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.debug("Logging initialized at DEBUG level.")
    logging.info("Logging initialized at INFO level.")


def get_config_from_ctx(ctx):
    """Helper function to get RPC URL, address, and private key from context."""
    return ctx.obj["rpc_url"], ctx.obj["address"], ctx.obj["private_key"]


CONTEXT_SETTINGS = cloup.Context.settings(
    # The following are parameters of Command:
    align_option_groups=False,
    align_sections=True,
    show_constraints=True,
    show_subcommand_aliases=True,
    # The following are parameters of HelpFormatter:
    formatter_settings=cloup.HelpFormatter.settings(
        max_width=100,
        col1_max_width=25,
        col2_min_width=30,
        indent_increment=3,
        col_spacing=3,
        # Place an empty line between definitions.
        row_sep="",
        theme=cloup.HelpTheme.dark(),
    ),
)


@cloup.group(aliases=["vbase"], context_settings=CONTEXT_SETTINGS)
@cloup.option("--verbose", is_flag=True, help="Increase verbosity.")
@cloup.pass_context
def cli(ctx, verbose):
    """vBase CLI for object commitment and verification"""
    # Initialize context to an empty dictionary
    # to provide a shared state that persists during the execution of a command
    # or across multiple subcommands within a CLI group.
    ctx.obj = {}
    # Initialize logging based on verbosity level.
    if verbose:
        setup_logging(1)


@cloup.group(
    aliases=["cs"],
    show_subcommand_aliases=True,
    show_constraints=True,
    help="Command group for interacting with a commitment service. "
    "Either a node commitment service or a forwarder commitment service must be used. ",
)
@cloup.option_group(
    "Node commitment service options",
    cloup.option("--vb-cs-node-rpc-url", help="vBase commitment service node RPC URL"),
    cloup.option(
        "--vb-cs-address", help="vBase commitment service smart contract address"
    ),
    help="Options for direct use of a commitment service provided a smart contract. "
    "The cmart contract must be accessed using an RPC URL of a blockchain node. ",
    constraint=cloup.constraints.all_or_none,
)
@cloup.option_group(
    "Forwarder commitment service options",
    cloup.option("--vb-forwarder-url", help="vBase forwarder URL"),
    cloup.option("--vb-api-key", help="vBase API key"),
    help="Options for use of a commitment service provided a smart contract "
    "via a vBase forwarder API service. "
    "vBase APIs abstract blockchain interaction and transaction costs. ",
    constraint=cloup.constraints.all_or_none,
)
@cloup.option_group(
    "Commitment service private key options",
    cloup.option("--vb-cs-private-key", help="vBase commitment service private key"),
    help="A private key is required for making commitments (adding objects). "
    "It is optional for verifying commiments. ",
    constraint=cloup.constraints.all_or_none,
)
@cloup.pass_context
def commitment_service(ctx, *args, **kwargs):
    config = load_config()
    print("commitment_service():")
    print("Loaded config:", pprint.pformat(config))
    print("kwargs:", pprint.pformat(kwargs))
    # Override command line arguments with config values if necessary.
    # Command line arguments take precedence over config values.
    args_config_dict = {
        "vb_api_key": "VBASE_API_KEY",
        "vb_cs_address": "VBASE_COMMITMENT_SERVICE_ADDRESS",
        "vb_cs_node_rpc_url": "VBASE_COMMITMENT_SERVICE_NODE_RPC_URL",
        "vb_cs_private_key": "VBASE_COMMITMENT_SERVICE_PRIVATE_KEY",
        "vb_forwarder_url": "VBASE_FORWARDER_URL",
    }
    for k, v in args_config_dict.items():
        if not kwargs[k]:
            kwargs[k] = config[v]
    print("Updated kwargs:", pprint.pformat(kwargs))
    # Connect to the node cs if the node RPC URL is provided..
    ctx.obj = {}
    if kwargs["vb_cs_node_rpc_url"]:
        ctx.obj["vbc"] = VBaseClient(
            Web3HTTPCommitmentService(
                node_rpc_url=kwargs["vb_cs_node_rpc_url"],
                commitment_service_address=kwargs["vb_cs_address"],
                private_key=kwargs["vb_cs_private_key"],
            )
        )
    elif kwargs["vb_forwarder_url"]:
        ctx.obj["vbc"] = VBaseClient(
            ForwarderCommitmentService(
                forwarder_url=kwargs["vb_forwarder_url"],
                api_key=kwargs["vb_api_key"],
                private_key=kwargs["vb_cs_private_key"],
            )
        )
    else:
        raise click.UsageError(
            "You must specify either --vb-cs-node-rpc-url or --vb-forwarder-url."
        )


cli.add_command(commitment_service)


@cloup.command(
    aliases=["ao"],
    show_constraints=True,
)
@cloup.option_group(
    "Object CID options",
    cloup.option("--object-cid", help="Specify object CID"),
    cloup.option("--object-cid-stdin", is_flag=True, help="Read object CID from stdin"),
    help="Options that define the content id (CID) for the object to be committed. ",
    constraint=cloup.constraints.RequireExactly(1),
)
@cloup.pass_context
def add_object(ctx, object_cid, object_cid_stdin):
    """Create an object commitment"""
    logging.info("Adding object...")
    print("add_object():")

    object_cid_value = get_object_cid(object_cid, object_cid_stdin)
    if not object_cid_value or not is_valid_cid(object_cid_value):
        raise click.UsageError("Bad object CID value.")
    print("object_cid_value =", object_cid_value)

    # Access vbc from ctx.
    if not "vbc" in ctx.obj or not ctx.obj["vbc"]:
        raise click.UsageError("VBaseClient is not defined. Check the configuration.")
    vbc = ctx.obj["vbc"]
    print("vbc =", pprint.pformat(vbc.__dict__))

    # Make the object commitment.
    receipt = vbc.add_object(object_cid_value)
    print("receipt =", pprint.pformat(receipt))


commitment_service.add_command(add_object)


@commitment_service.command()
@needs_object_cid_options
@cloup.pass_context
def verify_object(ctx, object_cid, object_cid_stdin):
    """Verify an object commitment"""
    logging.info("Verifying object...")

    object_cid_value = get_object_cid(object_cid, object_cid_stdin)
    if object_cid_value is None:
        return

    # Access global config from ctx.obj
    rpc_url, address, private_key = get_config_from_ctx(ctx)

    # TODO: Verify object


if __name__ == "__main__":
    cli()
