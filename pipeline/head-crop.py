from core import PDU

class HeadCrop(PDU):
    """ PDU that receives images and skeletons from Router 
        and crops images (head only) """

    QUEUE = 'head-crop'

    def process_message(self, message):
        # Route cropped images to face-recognition
        self.send_to('face-recognition', message)

if __name__ == "__main__":
    module = HeadCrop()
    module.run()
