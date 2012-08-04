import webcam
import time

def main():
    webcam_sampler = webcam.WebcamSensorSampler()
    webcam_consumer = webcam.WebcamDisplaySensorConsumer()
    webcam_sampler.start_sampling()
    webcam_consumer.start_consuming()
    time.sleep(100)
    webcam_sampler.stop_sampling()
    webcam_consumer.stop_consuming()
    
if __name__ == "__main__":
    main()