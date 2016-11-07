import logging
import re
from subprocess import check_output

from lib.files import random_file_name
from lib.image import base64_to_image

logger = logging.getLogger(__name__)


def save_image(image, width, height, prefix=None, decoder_name=None):
    """Given an image of width x height dimensions, flip it horizontally and
    save it to disk.

    Returns:
        the saved image path.
    """
    image = base64_to_image(image, width, height, decoder_name=decoder_name)
    temp_path = random_file_name('jpg', prefix=prefix)
    logger.info("Generated random path to save image: %s" % temp_path)

    image.save(temp_path)

    logger.info("Saved image to disk at path %s" % temp_path)
    return temp_path


def upload_to_s3(local_path):
    """diana@diana:~ $ s3cmd put test2.txt s3://ami-lab/test2.txt -P
       test2.txt -> s3://ami-lab/test2.txt  [1 of 1]
        0 of 0     0% in    0s     0.00 B/s  done
       Public URL of the object is: http://ami-lab.s3.amazonaws.com/test2.txt
    """
    s3_path = "s3://ami-lab/%s" % local_path.split('/')[-1]

    output = check_output(["s3cmd", "put", local_path, s3_path, "-P"])
    if not validate_output(output):
        logger.error("Unknown S3 output format: %r", output)

    return get_public_url(output)


def validate_output(output):
    """Assert S3 upload was successful and the output format is as expected:

    Output example:
    "File '/tmp/hello.txt' stored as 's3://ami-lab/hello.txt' (0 bytes in 0.5 seconds, -1.00 B/s) [1 of 1]\nPublic URL of the object is: http://ami-lab.s3.amazonaws.com/hello.txt\n"
    """
    regex = "File '[-\\/a-zA-Z0-9._]*' stored as '[-\\/a-zA-Z0-9.:_]*' \\([0-9]* bytes in [0-9.]* seconds, [-0-9.]* [k]*B\\/s\\) \\[[0-9]* of [0-9]*\\]\\nPublic URL of the object is: [-_.:\\/a-zA-Z0-9]*\\n"
    result = re.match(regex, output)
    match = result.group(0)

    if match and match == output:
        return True

    return False


def get_public_url(output):
    """Returns the uploaded file public S3 url."""
    return output.split()[-1]
