import cloup
from functools import update_wrapper, wraps
import logging

import cloup.constraints

from vbasecli.workers import add_object_worker, verify_object_worker
from vbasecli.config import OperationType, needs_config_options


def needs_object_cid_options(f):
    """Decorator to add shared input options for commands that require an object_cid."""

    @wraps(f)
    @cloup.option("--object-cid", help="Specify object CID")
    @cloup.option("--object-cid-stdin", is_flag=True, help="Read object CID from stdin")
    @cloup.pass_context
    def wrapper(ctx, *args, **kwargs):
        return ctx.invoke(f, ctx.obj, *args, **kwargs)

    return wrapper


def get_object_cid(object_cid, object_cid_stdin):
    """Helper function to get object_cid from argument or stdin."""
    # Handle object_cid and object_cid-stdin.
    object_cid_value = ""
    if object_cid:
        object_cid_value = object_cid
    elif object_cid_stdin:
        object_cid_value = cloup.get_text_stream("stdin").read()

    if not object_cid_value:
        cloup.echo("You must specify either--object-cid or --object-cid-stdin.")
        return None

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


@cloup.group(show_subcommand_aliases=True)
@cloup.option(
    "-v", "--verbose", count=True, help="Increase verbosity. Use -vv for debug output."
)
@cloup.pass_context
def cli(ctx, verbose):
    """vBase CLI for object commitment and verification"""
    # Initialize context to an empty dictionary
    # to provide a shared state that persists during the execution of a command
    # or across multiple subcommands within a CLI group.
    ctx.obj = {}
    # Initialize logging based on verbosity level.
    setup_logging(verbose)


@cloup.group(
    aliases=["cs"],
    show_subcommand_aliases=True,
    show_constraints=True,
    help="""
Command group for interacting with a commitment service.
Either a node commitment service or a forwarder commitment service must be used.
    """,
)
@cloup.option_group(
    "Node commitment service options",
    cloup.option("--vb-cs-node-rpc-url", help="vBase commitment service node RPC URL"),
    cloup.option(
        "--vb-cs-address", help="vBase commitment service smart contract address"
    ),
    help="""
Options for direct use of a commitment service provided a smart contract.
The cmart contract must be accessed using an RPC URL of a blockchain node.
""",
    constraint=cloup.constraints.all_or_none,
)
@cloup.option_group(
    "Forwarder commitment service options",
    cloup.option("--vb-forwarder-url", help="vBase forwarder URL"),
    cloup.option("--vb-api-key", help="vBase API key"),
    help="""
Options for use of a commitment service provided a smart contract
via a vBase forwarder API service.
vBase APIs abstract blockchain interaction and transaction costs.
""",
    constraint=cloup.constraints.all_or_none,
)
@cloup.option_group(
    "Commitment service private key options",
    cloup.option("--vb-cs-private-key", help="vBase commitment service private key"),
    help="""
A private key is required for making commitments (adding objects).
It is optional for verifying commiments.
""",
    constraint=cloup.constraints.all_or_none,
)
@cloup.pass_context
def commitment_service(ctx, *args, **kwargs):
    pass


cli.add_command(commitment_service)


@commitment_service.command()
@needs_object_cid_options
@cloup.pass_context
def add_object(ctx, object_cid, object_cid_stdin):
    """Create an object commitment"""
    logging.info("Adding object...")

    object_cid_value = get_object_cid(object_cid, object_cid_stdin)
    if object_cid_value is None:
        return

    # Access global config from ctx.obj
    rpc_url, address, private_key = get_config_from_ctx(ctx)

    # Add object using the worker function
    # add_object_worker(object_cid_value)
    pass


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

    # Verify object using the worker function
    # verify_object_worker(object_cid_value)
    pass


if __name__ == "__main__":
    cli()
