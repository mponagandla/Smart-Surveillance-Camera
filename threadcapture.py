from threading import Thread
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2

class VideoStr:
    def __init__(self,res, fps):
        
        self.camera= PiCamera()
        self.camera.resolution = res
        self.camera.framerate = fps
        self.rawCapture = PiRGBArray(self.camera, size= self.camera.resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        self.frame=None
        self.stopped=False

    def start(self):
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        for f in self.stream:
            self.img = f
            self.frame = f.array
            self.rawCapture.truncate(0)
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return
				
    def read(self):
        return self.frame

    def stop(self):
        self.stopped=True
        
    def clean(self):
        self.stream.close()
        self.rawCapture.close()
        self.camera.close()
    
