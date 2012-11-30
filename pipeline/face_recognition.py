from core import PDU

class FaceRecognition(PDU):
    """ PDU that receives cropped images (head only)
    and saves them to file """

    QUEUE = 'face-recognition'

    def process_message(self, message):
        # save image to file
        # now, don't do nothing
        pass
    
if __name__ == "__main__":
    module = FaceRecognition()
    module.run()
