import base64

from PIL import Image

def base64_to_image(data, width, height):
    """ Convert a base-64 image to an Image object
        from the PIL library. """
    decoded_string = base64.b64decode(data)
    return Image.frombuffer("RGB", (width, height), decoded_string).rotate(180)
        
def image_to_base64(image):
    """ Convert an image from PIL format to base64 for
        further processing down the pipeline. """
    image = image.rotate(180)
    return {
        'image': base64.b64encode(image.tostring()),
        'width': image.size[0],
        'height': image.size[1]
    }