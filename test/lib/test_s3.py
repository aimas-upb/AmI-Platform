import os
import sys
from unittest import TestCase

from mock import patch

from lib.s3 import upload_to_s3


class TestS3(TestCase):

    DEFAULT_OUTPUT = "File '/tmp/hello2.txt' stored as 's3://ami-lab/hello2.txt' (0 bytes in 0.7 seconds, -1.00 B/s) [1 of 1]\nPublic URL of the object is: http://ami-lab.s3.amazonaws.com/hello2.txt\n"

    @patch('lib.s3.check_output', return_value=DEFAULT_OUTPUT)
    def test_upload_image(self, _):
        """Assert uploading this test class file to S3 works as expected."""
        path = os.path.abspath(sys.modules[self.__module__].__file__)
        public_url = upload_to_s3(path)
        self.assertTrue(isinstance(public_url, str))
        self.assertTrue(public_url.startswith("http://"))
