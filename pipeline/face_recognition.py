from core import PDU
import struct

class FaceRecognition(PDU):
    """ PDU that receives cropped images (head only)
    and saves them to file """

    QUEUE = 'face-recognition'
    first_image = 0
    
    def process_message(self, message):
        # save first image to file
        if self.first_image == 0:
            self.print_image_to_file(message)
        self.first_image = 1
        # should send message to ip_power queue
        # params: ip, cmd, user, pwd
        
    def print_image_to_file(self, image_dict):
        # initiate header values
        d = {
            'mn1':66,
            'mn2':77,
            'filesize':0,
            'undef1':0,
            'undef2':0,
            'offset':54,
            'headerlength':40,
            'width': image_dict.get('width'),
            'height': image_dict.get('height'),
            'colorplanes':0,
            'colordepth':24,
            'compression':0,
            'imagesize':0,
            'res_hor':0,
            'res_vert':0,
            'palette':0,
            'importantcolors':0
        }
        
        crt_index=0;
        image = image_dict.get('cropped_image')
        
        # form array byte
        byte = bytes()
        for row in range(d['height']-1,-1,-1):
            # (BMPs are L to R from the bottom L row)
            for column in range(d['width']):
                print (crt_index)
                b = image[crt_index]
                g = image[crt_index+1]
                r = image[crt_index+2]
                crt_index = crt_index + 3
                pixel = struct.pack('<BBB',b,g,r)
                byte = byte + pixel
        
        # write .bmp image to file
        mn1 = struct.pack('<B',d['mn1'])
        mn2 = struct.pack('<B',d['mn2'])
        filesize = struct.pack('<L',d['filesize'])
        undef1 = struct.pack('<H',d['undef1'])
        undef2 = struct.pack('<H',d['undef2'])
        offset = struct.pack('<L',d['offset'])
        headerlength = struct.pack('<L',d['headerlength'])
        width = struct.pack('<L',d['width'])
        height = struct.pack('<L',d['height'])
        colorplanes = struct.pack('<H',d['colorplanes'])
        colordepth = struct.pack('<H',d['colordepth'])
        compression = struct.pack('<L',d['compression'])
        imagesize = struct.pack('<L',d['imagesize'])
        res_hor = struct.pack('<L',d['res_hor'])
        res_vert = struct.pack('<L',d['res_vert'])
        palette = struct.pack('<L',d['palette'])
        importantcolors = struct.pack('<L',d['importantcolors'])
        #create the outfile
        outfile = open('/home/ami/Desktop/bitmap_image.bmp','wb')
        #write the header + the bytes
        outfile.write(mn1+mn2+filesize+undef1+undef2+offset+headerlength+width+height+\
                      colorplanes+colordepth+compression+imagesize+res_hor+res_vert+\
                      palette+importantcolors+byte)
        outfile.close()
    
if __name__ == "__main__":
    module = FaceRecognition()
    module.run()
