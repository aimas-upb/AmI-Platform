import base64
import StringIO

from PIL import Image


def base64_to_image(data, width, height, decoder_name=None):
    """ Convert a base-64 image to an Image object
        from the PIL library. """
    if not decoder_name:
        decoder_name = 'raw'

    decoded_string = base64.b64decode(data)

    if decoder_name == 'jpg':
        return Image.open(StringIO.StringIO(decoded_string))
    else:
        return Image.frombuffer("RGB", (width, height), decoded_string, decoder_name)


def image_to_base64(image, encoder_name=None):
    """ Convert an image from PIL format to base64 for
        further processing down the pipeline. """
    image = image.rotate(180)

    #only raw is supported now
    encoder_name = "raw"
    return {
        'encoder_name': encoder_name,
        'image': base64.b64encode(image.tostring()),
        'width': image.size[0],
        'height': image.size[1]
    }
