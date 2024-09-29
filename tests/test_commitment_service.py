"""Test of the vBase CLI commitment service commands."""

import json
import re
import unittest
from click.testing import CliRunner
from parameterized import parameterized

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
            # Test using a local node RPC URL.
            (_LOCALHOST_COMMITMENT_SERVICE_ARGS,),
            # TODO: Test using a local forwarder URL.
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
        # Get the timestamp from the output.
        object_match = re.search(r"Added object = ({.*})", result.output, re.DOTALL)
        self.assertIsNotNone(object_match)
        json_str = object_match.group(1)
        self.assertIsNotNone(json_str)
        parsed_object = json.loads(json_str)
        timestamp = parsed_object["timestamp"]
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


if __name__ == "__main__":
    unittest.main()
