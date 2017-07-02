#from dropbox.client import DropboxOAuth2FlowNoRedirect
#from dropbox.client import DropboxClient
import GDriveAuth
from threadcapture import VideoStr
from googleapiclient.http import MediaFileUpload
from googleapiclient import discovery
import argparse
import imutils
import json
import time
import cv2
import datetime
import warnings
import httplib2




ap=argparse.ArgumentParser()
ap.add_argument("-c","--conf",required=True,help="Path to Json")
args=vars(ap.parse_args())

warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
vs = VideoStr(res= tuple(conf["resolution"]),fps= conf["fps"]).start()

#folderid = conf["drivefolder"]

credentials =  GDriveAuth.get_credentials()
http = credentials.authorize(httplib2.Http())
drive_service = discovery.build('drive', 'v3', http=http)

folder_meta = {'name': 'Mini Project/Raspberry Pi', 'mimeType' : 'application/vnd.google-apps.folder'}
folder = drive_service.files().create(body= folder_meta, fields='id').execute()
folderid = folder.get('id')
print("Folder Created : %s" % folder.get('id'))
	

print("Folder Loaded")
print ("[Info] Warming up")
time.sleep(2)
avg= None
lastUploaded = datetime.datetime.now()
motionCounter=0

#for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	#Grab Frame  frame = imutils.resize(frame, width=500)
while True:
	frame=vs.read()
	timestamp = datetime.datetime.now()
	text= "No Motion"

	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray,(21,21),0)
	
	if avg is None:
		avg= gray.copy().astype("float")
		continue
		
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta=cv2.absdiff(gray, cv2.convertScaleAbs(avg))
	
	thres = cv2.threshold(frameDelta, conf["deltathresh"], 255, cv2.THRESH_BINARY)[1]
	
	thres = cv2.dilate(thres, None, iterations=2)
	(_, cnts, _)=cv2.findContours(thres.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	for c in cnts:
		if cv2.contourArea(c) < conf["min_area"]:
			continue
			
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
		text="Motion Detected"
			
	ts = timestamp.strftime("%A %d %B %Y %I: %M:%s%p")
	cv2.putText(frame, "Room: {}".format(text),(10,10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
	cv2.putText(frame,ts,(10,frame.shape[0] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.35,(0,0,255),1) 
                                  	                                          
	if (timestamp - lastUploaded).seconds >= conf["min_upload_secs"]:
		if (text == "Motion Detected"):
			motionCounter+=1
			if (motionCounter >= conf["min_upload_frames"]):
				
				try:
					cv2.imwrite("image.png", frame)
				except Exception:
					print("Error writing")
				file_meta = {'name' : 'Motion Image Sample.jpg', 'parents' : [folderid]}
				media = MediaFileUpload("image.png", mimetype='image/png')
				file = drive_service.files().create(body= file_meta, media_body= media, fields= 'id').execute()
				print("Image Uploaded")			
		
	
	

vs.clean()
cv2.DestroyAllWindows()	
