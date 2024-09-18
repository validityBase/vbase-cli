import click
import logging

from vbasecli.workers import add_object_worker, verify_object_worker
from vbasecli.config import OperationType, global_options


def object_cid_options(f):
    """Decorator to add shared input options for commands that require an object_cid."""

    @click.option("--object_cid", help="Specify object CID")
    @click.option("--object_cid_stdin", is_flag=True, help="Read object CID from stdin")
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        return f(ctx, *args, **kwargs)

    return click.decorators.update_wrapper(new_func, f)


def get_object_cid(object_cid, object_cid_stdin):
    """Helper function to get object_cid from argument or stdin."""
    # Handle object_cid and object_cid_stdin.
    object_cid_value = ""
    if object_cid:
        object_cid_value = object_cid
    elif object_cid_stdin:
        object_cid_value = click.get_text_stream("stdin").read()

    if not object_cid_value:
        click.echo("You must specify either--object_cid or --object_cid_stdin.")
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


@click.group()
@click.option(
    "-v", "--verbose", count=True, help="Increase verbosity. Use -vv for debug output."
)
@click.pass_context
def cli(ctx, verbose):
    """vBase CLI for object commitment and verification"""
    # Initialize context to an empty dictionary
    # to provide a shared state that persists during the execution of a command
    # or across multiple subcommands within a CLI group.
    ctx.obj = {}
    setup_logging(verbose)


@click.command()
@click.pass_context
# Apply shared options to get the object CID to commit.
@object_cid_options
# This operation creates commitments and needs the global write config options.
# These options must be applied first for the wrappers to work correctly
# and click to provide the correct command help.
@global_options(OperationType.COMMIT)
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


@click.command()
@click.pass_context
# Apply shared options to get the object CID to verify.
@object_cid_options
# This operation creates commitments and needs the global write config options.
# These options must be applied first for the wrappers to work correctly
# and click to provide the correct command help.
@global_options(OperationType.VERIFY)
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


cli.add_command(add_object)
cli.add_command(verify_object)


if __name__ == "__main__":
    cli()
