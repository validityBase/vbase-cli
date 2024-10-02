"""Test of the vBase CLI commitment service commands."""

import click
import json
import re
import unittest
from click.testing import CliRunner
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


def get_timestamp_from_output(test_case: unittest.TestCase, output: str) -> str:
    """
    Get the timestamp from the output.

    :param output: The output string.
    :return: The timestamp.
    """
    object_match = re.search(r"Added object = ({.*})", output, re.DOTALL)
    test_case.assertIsNotNone(object_match)
    json_str = object_match.group(1)
    test_case.assertIsNotNone(json_str)
    parsed_object = json.loads(json_str)
    return parsed_object["timestamp"]


class TestCommitmentService(unittest.TestCase):
    """Test the VBase CLI commitment-service commands."""

    def setUp(self):
        """Set up a test runner and environment before each test."""
        self.runner = CliRunner()

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
        self.assertIn(f'Added object = {{"objectCid": "{TEST_HASH1}"', result.output)

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
        self.assertIn(f'Added object = {{"objectCid": "{TEST_HASH1}"', result.output)
        timestamp = get_timestamp_from_output(self, result.output)
        args_verify = args + [
            "verify-object",
            "--object-cid",
            TEST_HASH1,
            "--timestamp",
            timestamp,
        ]
        result = self.runner.invoke(cli, args_verify)
        self.assertEqual(result.exit_code, 0)
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
        self.assertIn(f'Added object = {{"objectCid": "{TEST_HASH1}"', result.output)
        timestamp = get_timestamp_from_output(self, result.output)
        # Add 5 seconds to the pd.Timestamp object.
        timestamp_5s_later = pd.Timestamp(timestamp) + pd.Timedelta("5s")
        # Verify that the verification failed with tight tolerance.
        args_verify = args + [
            "verify-object",
            "--object-cid",
            TEST_HASH1,
            "--timestamp",
            timestamp_5s_later,
        ]
        result = self.runner.invoke(cli, args_verify)
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Timestamp verification failed.", result.output)
        # Verify that the verification succeeded with looser tolerance.
        args_verify = args + [
            "verify-object",
            "--object-cid",
            TEST_HASH1,
            "--timestamp",
            timestamp_5s_later,
            "--timestamp-tol",
            "10s",
        ]
        result = self.runner.invoke(cli, args_verify)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Timestamp verification succeeded.", result.output)


if __name__ == "__main__":
    unittest.main()
