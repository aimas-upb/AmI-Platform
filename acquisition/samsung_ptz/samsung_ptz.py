import base64
import httplib
import json
import logging
from StringIO import StringIO
import time

import kestrel
from PIL import Image
import requests
from requests.auth import HTTPDigestAuth

from lib.log import setup_logging
from core.settings import KESTREL_SERVERS

logger = logging.getLogger(__name__)

def image_to_base64(image):
    """ Convert an image from PIL format to base64 for
        further processing down the pipeline. """

    return {
        "created_at" : int(time.time()),
        "context" : "",
        "sensor_type" : "ptz",
        "sensor_id" : "samsumg_ptz",
        "sensor_position" : [0, 0, 0],
        "type" : "image_rgb",
        "image_rgb": {
            "encoder_name" : "jpg",
            "image" : base64.b64encode(image.tostring()),
            "width" : image.size[0],
            "height": image.size[1]
        }
    }


def make_ptz_cam_http_request():
    # 'msubmenu=jpg' is required,
    # resolution: 1 (640x480), 3 (320x240); frate: 1 - 25)
    params = {'msubmenu' : 'mjpg' , 'profile' : '1', 'resolution' : '1',
              'frate' : '25', 'compression' : '1'}
    username = 'admin'
    password = '4321'
    camera_url = 'http://172.16.4.118/cgi-bin/video.cgi'

    logger.info("Making HTTP request for PTZ camera..")

    requests.get(camera_url,
                 params=params,
                 auth=HTTPDigestAuth(username,password),
                 hooks=dict(response=response_hook))

def get_header(chunk):
    """ Given a chunk of data from the iter_chunks iterator that
    fetches the chunks from the server, extract the header (if any) from it.

    Return the header iff it exists, and None otherwise.

    """

    if "--Samsung" or "Content" in chunk:
        header = chunk[chunk.find("--Samsung"):chunk.find("\n\r")]
        if header:
            return header

    return None

def get_before_header(chunk):
    """ Return the content __BEFORE__ the header in a given chunk.
    It's useful in order to complete the last frame. """
    return chunk[:chunk.find("--Samsung")].strip('\n\r')

def get_after_header(chunk):
    """ Return the content __AFTER__ the header in a given chunk.
    It's useful in order to start a new frame. """
    return chunk[chunk.find("--Samsung")+68:].strip('\n\r')

def iter_frames():
    try:
        request = make_ptz_cam_http_request()

        content = ""
        frames = 0

        for chunk in request.iter_chunks():

            # Skip empty chunks
            if not chunk:
                logger.warn("Got empty chunk!")
                continue

            header = get_header(chunk)
            if header:
                logger.info("Found header within chunk.")                

                # If a header has been found, first we complete the last frame
                content += get_before_header(chunk)

                # Check if it's the first received header ever, so we don't
                # have any actual valid content before that.
                if frames > 0:
                    try:
                        img = Image.open(StringIO(content))
                        yield image_to_base64(img)
                    except IOError:
                        logger.exception("Encountered corrupted frame")
                        continue

                frames += 1
                content = get_after_header(chunk)
            else:
                logger.info("Chunk without header here")
                content += chunk	# chunk without header

    except requests.ConnectionError:
        logger.exception("Cannot connect to PTZ camera")

def response_hook(response, *args, **kwargs):
    logger.info("Response hook is being called")
    response.iter_chunks = lambda amt=None: iter_chunks(response.raw._fp, amt=amt)
    return response

def iter_chunks(response, amt=None):
    """
    A copy-paste version of httplib.HTTPConnection._read_chunked() that
    yields chunks served by the server.
    """
    if response.chunked:
        while True:
            line = response.fp.readline().strip()
            arr = line.split(';', 1)
            try:
                chunk_size = int(arr[0], 16)
            except ValueError:
                response.close()
                raise httplib.IncompleteRead(chunk_size)
            if chunk_size == 0:
                break
            value = response._safe_read(chunk_size)
            yield value
            # we read the whole chunk, get another
            response._safe_read(2)      # toss the CRLF at the end of the chunk

        # read and discard trailer up to the CRLF terminator
        ### note: we shouldn't have any trailers!
        while True:
            line = response.fp.readline()
            if not line:
                # a vanishingly small number of sites EOF without
                # sending the trailer
                break
            if line == '\r\n':
                break

        # we read everything; close the "file"
        response.close()
    else:
        # Non-chunked response. If amt is None, then just drop back to
        # response.read()
        if amt is None:
            yield response.read()
        else:
            # Yield chunks as read from the HTTP connection
            while True:
                ret = response.read(amt)
                if not ret:
                    break
                yield ret

if __name__ == '__main__':
    setup_logging()
    kestrel_client = kestrel.Client(KESTREL_SERVERS)
    for image in iter_frames():
        measurement = json.dumps(image)
        kestrel_client.add('measurements', measurement)
        logger.info("Added a frame of size %d" % len(measurement))
