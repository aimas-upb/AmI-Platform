from core import PDU

import time
from sklearn.externals import joblib

from subprocess import check_call

from lib.log import setup_logging
from lib.skeleton_features import all_features

class PostureClassifier(PDU):
    QUEUE = 'posture-classifier'
    
    def __init__(self, **kwargs):
        super(PostureClassifier, self).__init__(**kwargs)
        self.classifier = self.load_classifier()
        self.classifier.n_jobs
        self.classes = {}
        self.init_classes()

    def process_message(self, message):
        if message['type'] !=  'skeleton':
            return
        
        age = time.time() - message['created_at'] / 1000
        if age > 10.0:
            self.log('Dropping old message. Age was: %f' % age)
            return 
        
        features = all_features(message['skeleton_3D'])
        'we just classify one example'
        posture_probas = self.classifier.predict_proba([features])[0]
        possible_features = self.possible_postures(posture_probas)
        if len(possible_features) > 0:
            log_msg = ", ".join(['%s with %f' % pair for pair in possible_features])
            self.log("Got %s, %f s ago from %s" % (log_msg, age, message['sensor_id']))

    def possible_postures(self, probas):
        return [(self.classes[i], probas[i]) for i in range(len(probas)) if (probas[i] > 0.50)]

    def load_classifier(self):
        url = ' https://www.dropbox.com/sh/k8liek6yqii5gvo/AADm0FcdrInllRuNMelYUNYSa/posture_classifier_data.joblib.pkl'
        tmp_file = '/tmp/clasifier_data.joblib.pkl'
        command = 'wget %s -O %s -o /tmp/wget.log' % (url, tmp_file)
        self.log("Downloading with %s" % command)
        check_call(command,  shell=True)
        self.log("loading classifier from %s" % tmp_file)
        return joblib.load(tmp_file)
    
    ' Attention, MAGIC NUMBERS AHEAD!'
    def init_classes(self):
        self.classes[0]  = 'Bf_both_up'            
        self.classes[1]  = 'BF_down_down'            
        self.classes[2]  = 'BF_down_lateral'        
        self.classes[3]  = 'BF_frontal_frontal'        
        self.classes[4]  = 'BF_frontal_lateral'        
        self.classes[5]  = 'BF_frontal_up'        
        self.classes[6]  = 'BF_lateral_down'        
        self.classes[7]  = 'BF_lateral_frontal'        
        self.classes[8]  = 'BF_lateral_lateral'        
        self.classes[9]  = 'BF_lateral_up'        
        self.classes[10] = 'BF_left_frontal'        
        self.classes[11] = 'BF_left_up'            
        self.classes[12] = 'BF_right_frontal'        
        self.classes[13] = 'BF_right_up'            
        self.classes[14] = 'BF_up_frontal'        
        self.classes[15] = 'BF_up_lateral'        
        self.classes[16] = 'sit_both_up'            
        self.classes[17] = 'sit_down_down'        
        self.classes[18] = 'sit_down_lateral'        
        self.classes[19] = 'sit_frontal_frontal'        
        self.classes[20] = 'sit_frontal_lateral'        
        self.classes[21] = 'sit_frontal_up'        
        self.classes[22] = 'sit_lateral_down'        
        self.classes[23] = 'sit_lateral_frontal'        
        self.classes[24] = 'sit_lateral_lateral'        
        self.classes[25] = 'sit_lateral_up'        
        self.classes[26] = 'sit_left_frontal'        
        self.classes[27] = 'sit_left_up'            
        self.classes[28] = 'sit_right_frontal'        
        self.classes[29] = 'sit_right_up'            
        self.classes[30] = 'sit_up_frontal'        
        self.classes[31] = 'sit_up_lateral'        
        self.classes[32] = 'upright_both_up'        
        self.classes[33] = 'upright_down_down'        
        self.classes[34] = 'upright_down_lateral'        
        self.classes[35] = 'upright_frontal_frontal'    
        self.classes[36] = 'upright_frontal_lateral'    
        self.classes[37] = 'upright_frontal_up'        
        self.classes[38] = 'upright_lateral_down'        
        self.classes[39] = 'upright_lateral_frontal'    
        self.classes[40] = 'upright_lateral_lateral'    
        self.classes[41] = 'upright_lateral_up'        
        self.classes[42] = 'upright_left_frontal'        
        self.classes[43] = 'upright_left_up'        
        self.classes[44] = 'upright_right_frontal'    
        self.classes[45] = 'upright_right_up'        
        self.classes[46] = 'upright_up_frontal'        
        self.classes[47] = 'upright_up_lateral'        

    
if __name__ == "__main__":
    setup_logging()
    module = PostureClassifier()
    module.run()
    

