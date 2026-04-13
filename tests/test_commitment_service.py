"""Test of the vBase CLI commitment service commands."""

import json
import re
import time
import unittest
from click.testing import CliRunner, Result
from parameterized import parameterized
import pandas as pd

from vbasecli.cli import cli


# TODO: This function is duplicated in vbase. Refactor to avoid duplication.
def int_to_hash(n: int) -> str:
    """
    Convert an integer to a hash string.

    :param n: The integer.
    :return: The resulting hash string.
    """
    return "0x" + f"{n:X}".rjust(64, "0")


# Hash constants used in various tests.
TEST_HASH1 = int_to_hash(1)
TEST_HASH2 = int_to_hash(100)

# Localhost commitment service config.
_LOCALHOST_COMMITMENT_SERVICE_ARGS = [
    "commitment-service",
    "--vb-cs-node-rpc-url",
    "http://127.0.0.1:8545",
    "--vb-cs-address",
    "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
    "--vb-cs-private-key",
    "0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e",
]

# CLI output excerpt length when raising parse errors (keeps CI logs readable).
_OUTPUT_EXCERPT_MAX_CHARS = 1200


def _truncate_output_for_exc(
    output: str, max_chars: int = _OUTPUT_EXCERPT_MAX_CHARS
) -> str:
    """Return output or a head excerpt plus omitted length for exception messages."""
    if len(output) <= max_chars:
        return output
    omitted = len(output) - max_chars
    return f"{output[:max_chars]}\n... ({omitted} more characters)"


def parse_added_object_json(output: str) -> dict:
    """
    Parse the JSON object printed after 'Added object = '.

    Key order and pretty-printing in the CLI output must not affect tests.
    """
    object_match = re.search(r"Added object = ({.*})", output, re.DOTALL)
    if object_match is None:
        excerpt = _truncate_output_for_exc(output)
        raise ValueError(
            "No 'Added object = {...}' JSON in output. Excerpt:\n" + excerpt
        )
    return json.loads(object_match.group(1))


def assert_object_cid_matches(
    test_case: unittest.TestCase, added: dict, expected_cid: str
) -> None:
    """Assert parsed JSON contains objectCid and it matches expected (clear failures)."""
    test_case.assertIn(
        "objectCid",
        added,
        msg=f"parsed JSON keys: {sorted(added.keys())}",
    )
    test_case.assertEqual(added["objectCid"], expected_cid)


def wait_until_verify_succeeds(
    runner: CliRunner,
    args_verify: list[str],
    *,
    timeout_sec: float = 30.0,
    poll_interval_sec: float = 0.25,
) -> Result:
    """
    Poll verify-object until exit 0 or timeout.

    Chain/indexing can lag add-object; this avoids fixed sleeps and reduces CI flakiness.
    """
    deadline = time.monotonic() + timeout_sec
    last_result = None
    while time.monotonic() < deadline:
        last_result = runner.invoke(cli, args_verify)
        if last_result.exit_code == 0:
            return last_result
        time.sleep(poll_interval_sec)
    excerpt = _truncate_output_for_exc(last_result.output if last_result else "")
    raise AssertionError(
        f"verify-object did not succeed within {timeout_sec}s. "
        f"Last exit_code={getattr(last_result, 'exit_code', None)}. Output excerpt:\n"
        f"{excerpt}"
    )


def get_timestamp_from_output(test_case: unittest.TestCase, output: str) -> str:
    """
    Get the timestamp from the output.

    Normalizes to ISO-8601 so --timestamp receives a stable string for pd.Timestamp.
    """
    parsed_object = parse_added_object_json(output)
    test_case.assertIn("timestamp", parsed_object)
    return pd.Timestamp(parsed_object["timestamp"]).isoformat()


class TestCommitmentService(unittest.TestCase):
    """Test the VBase CLI commitment-service commands."""

    def setUp(self):
        """Set up a test runner and environment before each test."""
        self.runner = CliRunner(mix_stderr=True)

    @parameterized.expand(
        [
            # Test using a local node RPC URL.
            (_LOCALHOST_COMMITMENT_SERVICE_ARGS,),
            # TODO: Test using a local forwarder URL.
        ]
    )
    def test_add_object_with_object_cid(self, args):
        """Test the add_object command with object_cid."""
        args_add = args + [
            "add-object",
            "--object-cid",
            TEST_HASH1,
        ]
        result = self.runner.invoke(cli, args_add)
        self.assertEqual(result.exit_code, 0)
        added = parse_added_object_json(result.output)
        assert_object_cid_matches(self, added, TEST_HASH1)

    @parameterized.expand(
        [
            (_LOCALHOST_COMMITMENT_SERVICE_ARGS,),
        ]
    )
    def test_add_verify_object_with_object_cid(self, args):
        """Test the add_object command with object_cid followed by verify_object."""
        args_add = args + [
            "add-object",
            "--object-cid",
            TEST_HASH1,
        ]
        result = self.runner.invoke(cli, args_add)
        self.assertEqual(result.exit_code, 0)
        added = parse_added_object_json(result.output)
        assert_object_cid_matches(self, added, TEST_HASH1)
        timestamp = get_timestamp_from_output(self, result.output)
        args_verify = args + [
            "verify-object",
            "--object-cid",
            TEST_HASH1,
            "--timestamp",
            timestamp,
        ]
        result = wait_until_verify_succeeds(self.runner, args_verify)
        self.assertIn("Timestamp verification succeeded.", result.output)

    @parameterized.expand(
        [
            (_LOCALHOST_COMMITMENT_SERVICE_ARGS,),
        ]
    )
    def test_add_verify_object_with_object_cid_padding(self, args):
        """Test the add_object command with object_cid followed by verify_object."""
        args_add = args + [
            "add-object",
            "--object-cid",
            TEST_HASH1[15:],
            "--pad-object-cid",
        ]
        result = self.runner.invoke(cli, args_add)
        self.assertEqual(result.exit_code, 0)
        added = parse_added_object_json(result.output)
        assert_object_cid_matches(self, added, TEST_HASH1)
        timestamp = get_timestamp_from_output(self, result.output)
        args_verify = args + [
            "verify-object",
            "--object-cid",
            TEST_HASH1[15:],
            "--pad-object-cid",
            "--timestamp",
            timestamp,
        ]
        result = wait_until_verify_succeeds(self.runner, args_verify)
        self.assertIn("Timestamp verification succeeded.", result.output)

    @parameterized.expand(
        [
            (_LOCALHOST_COMMITMENT_SERVICE_ARGS,),
        ]
    )
    def test_add_verify_object_with_object_cid_timestamp_tolerance(self, args):
        """Test the add_object command with object_cid followed by verify_object
        with timestamp tolerance."""
        args_add = args + [
            "add-object",
            "--object-cid",
            TEST_HASH1,
        ]
        result = self.runner.invoke(cli, args_add)
        self.assertEqual(result.exit_code, 0)
        added = parse_added_object_json(result.output)
        assert_object_cid_matches(self, added, TEST_HASH1)
        timestamp = get_timestamp_from_output(self, result.output)
        args_verify_ok = args + [
            "verify-object",
            "--object-cid",
            TEST_HASH1,
            "--timestamp",
            timestamp,
        ]
        wait_until_verify_succeeds(self.runner, args_verify_ok)
        timestamp_5s_later = (pd.Timestamp(timestamp) + pd.Timedelta("5s")).isoformat()
        args_verify = args + [
            "verify-object",
            "--object-cid",
            TEST_HASH1,
            "--timestamp",
            timestamp_5s_later,
        ]
        result = self.runner.invoke(cli, args_verify)
        self.assertEqual(result.exit_code, 1, msg=result.output)
        self.assertIn("Timestamp verification failed.", result.output)
        args_verify = args + [
            "verify-object",
            "--object-cid",
            TEST_HASH1,
            "--timestamp",
            timestamp_5s_later,
            "--timestamp-tol",
            "10s",
        ]
        result = wait_until_verify_succeeds(self.runner, args_verify)
        self.assertIn("Timestamp verification succeeded.", result.output)


if __name__ == "__main__":
    unittest.main()
