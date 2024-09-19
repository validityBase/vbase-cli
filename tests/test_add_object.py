import unittest
from click.testing import CliRunner
from parameterized import parameterized

from vbasecli.vbase import cli


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


class TestVBaseCLI(unittest.TestCase):

    def setUp(self):
        """Set up a test runner and environment before each test."""
        self.runner = CliRunner()

    @parameterized.expand(
        [
            # Test using a local node RPC URL.
            (
                [
                    "commitment-service",
                    "--vb-cs-node-rpc-url",
                    "http://127.0.0.1:8545",
                    "--vb-cs-address",
                    "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
                    "--vb-cs-private-key",
                    "0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e",
                ],
            ),
            # TODO: Test using a local forwarder URL.
        ]
    )
    def test_add_object_with_object_cid(self, args):
        """Test the add_object command with object_cid."""
        with self.runner.isolated_filesystem():
            args = [
                "commitment-service",
                "--vb-cs-node-rpc-url",
                "http://127.0.0.1:8545",
                "--vb-cs-address",
                "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
                "--vb-cs-private-key",
                "0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e",
                "add-object",
                "--object-cid",
                "0x0a247bc6e60fd864fee095dc892f5c5ae155db244e2f91097de4279240033749",
            ]
            result = self.runner.invoke(cli, args)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Adding object...", result.output)


if __name__ == "__main__":
    unittest.main()
