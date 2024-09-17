import click

from vbasecli.workers import add_object_worker, verify_object_worker
from vbasecli.config import global_options


def shared_object_cid_options(f):
    """Decorator to add shared input options for commands that require an object_cid."""

    @click.option("--object_cid", help="Specify object CID")
    @click.option("--object_cid_stdin", is_flag=True, help="Read object CID from stdin")
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        return f(ctx, *args, **kwargs)

    return click.decorators.update_wrapper(new_func, f)


def get_object_cid(object_cid, object_cid_stdin):
    """Helper function to get object_cid from argument or stdin."""
    content = ""

    # Handle object_cid and object_cid_stdin.
    object_cid_value = ""
    if object_cid:
        object_cid_value = object_cid
    elif object_cid_stdin:
        object_cid_value = click.get_text_stream("stdin").read()

    if not object_cid_value:
        click.echo("No valid input provided. Use --object_cid or --object_cid_stdin.")
        return None

    return object_cid_value


def get_config_from_ctx(ctx):
    """Helper function to get RPC URL, address, and private key from context."""
    return ctx.obj["rpc_url"], ctx.obj["address"], ctx.obj["private_key"]


@click.group()
@click.pass_context
def cli(ctx):
    """vbase CLI for object commitment and verification"""
    ctx.obj = {}  # Initialize context object


@cli.command()
# This operation creates commitments and needs the global write config options.
@global_options
# Apply shared options to get the object CID to commit.
@shared_object_cid_options
@click.pass_context
def add_object(ctx, file, stdin, object_cid, object_cid_stdin):
    """Create an object commitment"""

    object_cid_value = get_object_cid(file, stdin, object_cid, object_cid_stdin)
    if object_cid_value is None:
        return

    # Access global config from ctx.obj
    rpc_url, address, private_key = get_config_from_ctx(ctx)

    # Add object using the worker function
    add_object_worker(object_cid_value)


@cli.command()
# This operation creates commitments and needs the global write config options.
@global_options
# Apply shared options to get the object CID to commit.
@shared_object_cid_options
@click.pass_context
def verify_object(ctx, file, stdin, object_cid, object_cid_stdin):
    """Verify an object commitment"""
    object_cid_value = get_object_cid(file, stdin, object_cid, object_cid_stdin)
    if object_cid_value is None:
        return

    # Access global config from ctx.obj
    rpc_url, address, private_key = get_config_from_ctx(ctx)

    # Verify object using the worker function
    verify_object_worker(object_cid_value)


if __name__ == "__main__":
    cli()
