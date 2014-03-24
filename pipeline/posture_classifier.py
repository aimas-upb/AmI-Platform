from core import PDU

from sklearn.externals import joblib

from lib.log import setup_logging
from lib.skeleton_features import all_features

class PostureClassifier(PDU):
    QUEUE = 'posture_classifier'
    
    def __init__(self, **kwargs):
        super(PostureClassifier, self).__init__(**kwargs)
        self.classifier = self.load_classifier()

    def process_message(self, message):
        if message['type'] !=  'skeleton':
            return
        
        features = all_features(message['skeleton_3D'])
        posture = self.classifier.predict([features])
         
        
        pass


    def load_classifier(self):
        filename = '/home/ami/AmI-Platform/resources/posture_classifier_data.joblib'
        self.log("loading classifier from %s" % filename)
        return joblib.load(filename)
    
if __name__ == "__main__":
    setup_logging()
    module = PostureClassifier()
    module.run()
    

