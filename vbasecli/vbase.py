#!/usr/bin/python3

"""vBase CLI for object commitment and verification"""

from functools import wraps
import logging
import pprint
import re
import click
import cloup
import pandas as pd

from vbase import (
    get_default_logger,
    VBaseClient,
    Web3HTTPCommitmentService,
    IndexingService,
    ForwarderCommitmentService,
)

from vbasecli.config import load_config


LOG = get_default_logger(__name__)


def setup_logging(verbosity):
    """Set up logging based on verbosity level."""

    # Control logging level based on verbosity
    if verbosity == 0:
        LOG.setLevel(logging.WARNING)
    elif verbosity == 1:
        LOG.setLevel(logging.INFO)
    else:
        LOG.setLevel(logging.DEBUG)


def verify_object_cid_value(s):
    """Check if a string is a valid CID."""

    if not s:
        raise click.UsageError("Undefined object CID value.")
    # Regular expression to match a valid CID.
    # A CID is a 256-byte (64-hex digit) string in hex representation.
    # It stats with '0x' and be followed by 64 hexadecimal characters.
    pattern = r"^0x[0-9a-fA-F]{64}$"
    if not re.match(pattern, s):
        raise click.UsageError(
            f'Invalid object CID value: "{s}". '
            "Please specify a valid 256-bit hex string."
        )


def verify_timestamp_value(s):
    """Check if a string is a valid timestamp."""

    if not s:
        raise click.UsageError("Undefined timestamp value.")
    try:
        pd.Timestamp(s)
    except ValueError as exc:
        raise click.UsageError(
            f'Invalid timestamp value: "{s}". '
            "Please specify a valid timestamp compatible with pd.Timestamp()."
        ) from exc


def needs_object_cid_options(f):
    """Decorator to add shared input options for commands that require an object_cid."""

    @wraps(f)
    @cloup.option("--object-cid", help="Specify object CID")
    @cloup.option("--object-cid-stdin", is_flag=True, help="Read object CID from stdin")
    def wrapper(ctx, *args, **kwargs):
        return ctx.invoke(f, ctx, *args, **kwargs)

    return wrapper


def get_object_cid(
    object_cid: str, object_cid_stdin: str, l_stdin_text_stream: list[str]
) -> tuple[str, list[str]]:
    """Helper function to get object_cid from argument or stdin."""
    # Handle object_cid and object_cid-stdin.
    object_cid_value = ""
    if object_cid:
        object_cid_value = object_cid
    elif object_cid_stdin:
        object_cid_value = l_stdin_text_stream[0].strip()
        l_stdin_text_stream = l_stdin_text_stream[1:]
    else:
        raise click.UsageError(
            "You must specify either --object-cid or --object-cid-stdin."
        )

    if not object_cid_value:
        raise click.UsageError("Undefined object CID value.")

    # Strip leading and trailing whitespace to make sure the CID is clean
    # and hex string -> bytes conversion works correctly.
    object_cid_value = object_cid_value.strip()
    # Add '0x' prefix to the hex object cid if it is missing.
    if not object_cid_value.startswith("0x"):
        object_cid_value = "0x" + object_cid_value

    verify_object_cid_value(object_cid_value)

    LOG.info("get_object_cid(): object_cid_value = %s", object_cid_value)

    return object_cid_value, l_stdin_text_stream


def get_timestamp(
    timestamp: str, timestamp_stdin: str, l_stdin_text_stream: list[str]
) -> tuple[pd.Timestamp, list[str]]:
    """Helper function to get timestamp from argument or stdin."""
    # Handle timestamp and timestamp-stdin.
    timestamp_value = ""
    if timestamp:
        timestamp_value_str = timestamp
    elif timestamp_stdin:
        timestamp_value_str = l_stdin_text_stream[0].strip()
        l_stdin_text_stream = l_stdin_text_stream[1:]
    else:
        raise click.UsageError(
            "You must specify either --timestamp or --timestamp-stdin."
        )

    verify_timestamp_value(timestamp_value_str)
    timestamp_value = pd.Timestamp(timestamp_value_str)

    LOG.info("get_timestamp(): timestamp_value = %s", timestamp_value)

    return timestamp_value, l_stdin_text_stream


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
@cloup.option("-v", "--verbose", count=True, help="Increase verbosity level")
@cloup.pass_context
def cli(ctx, verbose):
    """vBase CLI for object commitment and verification"""

    setup_logging(verbose)
    LOG.info("Logging level: %s", logging.getLogger().getEffectiveLevel())

    # Initialize context to an empty dictionary
    # to provide a shared state that persists during the execution of a command
    # or across multiple subcommands within a CLI group.
    ctx.obj = {}


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
def commitment_service(ctx, **kwargs):
    """Command group for interacting with a commitment service."""

    config = load_config()
    LOG.debug("commitment_service(): config = %s", config)
    LOG.debug("commitment_service(): kwargs = %s", kwargs)
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
    LOG.debug("commitment_service(): Updated kwargs =%s", kwargs)
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
# TODO: Move this to a common decorator.
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

    LOG.info("Adding object...")

    # Get the stdin input stream in case it is used to define parameters.
    # This is necessary because click.get_text_stream("stdin") can only be called once.
    # The callees of get_object_cid() and get_timestamp() will use this stream
    # and advance through it if they consume its values.
    l_stdin_text_stream = click.get_text_stream("stdin").read().split()
    object_cid_value, l_stdin_text_stream = get_object_cid(
        object_cid, object_cid_stdin, l_stdin_text_stream
    )

    # TODO: Factor out common code.
    # Access vbc from ctx.
    if not "vbc" in ctx.obj or not ctx.obj["vbc"]:
        raise click.UsageError("VBaseClient is not defined. Check the configuration.")
    vbc = ctx.obj["vbc"]

    # Make the object commitment.
    receipt = vbc.add_object(object_cid_value)
    click.echo("Added object =" + pprint.pformat(receipt))


commitment_service.add_command(add_object)


def fail(msg: str):
    """Helper function to print an error message and raise a click exception."""
    click.secho(msg, fg="red", err=True)
    raise click.ClickException(msg)


@cloup.command(
    aliases=["vo"],
    show_constraints=True,
)
# TODO: Move this to a common decorator.
@cloup.option_group(
    "Object CID options",
    cloup.option("--object-cid", help="Specify object CID"),
    cloup.option("--object-cid-stdin", is_flag=True, help="Read object CID from stdin"),
    help="Options that define the content id (CID) for the object to be committed. ",
    constraint=cloup.constraints.RequireExactly(1),
)
@cloup.option_group(
    "Timestamp verification options",
    cloup.option("--timestamp", help="Commitment timestamp"),
    cloup.option("--timestamp-stdin", is_flag=True, help="Read timestamp from stdin"),
    cloup.option("--timestamp-tol", help="Tolerance for commitment timestamp"),
    help="Options that define the commitment timestamp and its tolerance. ",
    # TODO: Add a constraint that tol alone is not allowed.
)
@cloup.pass_context
# The commands must take a large number of arguments.
# pylint: disable=too-many-arguments
def verify_object(
    ctx, object_cid, object_cid_stdin, timestamp, timestamp_stdin, timestamp_tol
):
    """Verify an object commitment"""

    LOG.info("Verifying object...")

    l_stdin_text_stream = click.get_text_stream("stdin").read().split()
    object_cid_value, l_stdin_text_stream = get_object_cid(
        object_cid, object_cid_stdin, l_stdin_text_stream
    )
    timestamp_value, l_stdin_text_stream = get_timestamp(
        timestamp, timestamp_stdin, l_stdin_text_stream
    )

    # TODO: Factor out common code.
    # Access vbc from ctx.
    if not "vbc" in ctx.obj or not ctx.obj["vbc"]:
        raise click.UsageError("VBaseClient is not defined. Check the configuration.")
    vbc = ctx.obj["vbc"]

    # Find all object commitments for user and object.
    indexing_service = IndexingService.create_instance_from_commitment_service(
        vbc.commitment_service
    )
    # TODO: Add find_user_object() and call that instead.
    l_objects = indexing_service.find_objects(object_cid_value)
    if len(l_objects) == 0:
        fail("No matching objects found.")

    # Find the closest commitment to the target timestamp.
    # Convert timestamps in the list to pd.Timestamp objects and find the closest one.
    closest_object = min(
        l_objects, key=lambda x: abs(pd.Timestamp(x["timestamp"]) - timestamp_value)
    )

    # TODO: Technically, one of the other commitments may be close enough and valid.
    # We could traverse the list and verify each one until we find a successful verification.
    # This would be more robust but this simple implementation works well enough
    # for secure indexing services.

    # Verify the commitment for this object. Just because it came from the indexing service
    # does not mean it has a commitment service commitment.
    ret = vbc.verify_user_object(
        vbc.get_default_user(), object_cid_value, closest_object["timestamp"]
    )
    if not ret:
        fail("Commitment verification failed.")

    # Verify the timedelta for the closest commitment.
    # TODO: Clarify that default tolerance is 1 second.
    if not timestamp_tol:
        timestamp_tol = pd.Timedelta("1s")
    if pd.Timestamp(closest_object["timestamp"]) - timestamp_value > pd.Timedelta(
        timestamp_tol
    ):
        fail("Timestamp verification failed.")

    click.echo("Found object commitment = " + pprint.pformat(closest_object))
    click.echo("Timestamp verification succeeded.")


commitment_service.add_command(verify_object)


if __name__ == "__main__":
    cli.main(prog_name="vbase")
