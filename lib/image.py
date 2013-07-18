import base64
import StringIO

from PIL import Image

def base64_to_image(data, width, height, decoder_name = 'raw'):
    """ Convert a base-64 image to an Image object
        from the PIL library. """
    decoded_string = base64.b64decode(data)
#    print "decoder" , decoder_name, len(data)
    if decoder_name in ['jpg', 'jpeg']:
        return Image.open(StringIO.StringIO(decoded_string))
    else: 
        return Image.frombuffer("RGB", (width, height), decoded_string, decoder_name).rotate(180)
        
def image_to_base64(image, encoder_name = 'raw'):
    """ Convert an image from PIL format to base64 for
        further processing down the pipeline. """
    
    if encoder_name in ['jpg', 'jpeg']:
        buf = StringIO.StringIO()
        image.save(buf, 'jpeg')
        encoder_name = 'jpeg'
        image_data = buf.getvalue()
    else: 
        image_data = image.tostring()
    
    return {
        'encoder_name': encoder_name,
        'image': base64.b64encode(image_data),
        'width': image.size[0],
        'height': image.size[1]
    }