import cv2
import numpy as np
import face_recognition as face_rec
import os
import pyttsx3 as textSpeach
from datetime import  datetime
import pymongo

engine = textSpeach.init()

myclient = pymongo.MongoClient("mongodb+srv://mongodb_pro:NbQEQy3Ao3yP63RV@cluster0.oxclotd.mongodb.net/")

mydb = myclient["MCA"]
dblist = myclient.list_database_names()
if "MCA" in dblist:
  str="Database ready."
  print(str)
  engine.say(str)
  engine.runAndWait()
  
mycol = mydb["attendance"]


def resize(img, size) :
    width = int(img.shape[1]*size)
    height = int(img.shape[0] * size)
    dimension = (width, height)
    return cv2.resize(img, dimension, interpolation= cv2.INTER_AREA)

path = 'images'
staff_img = []
staff_name = []
myList = os.listdir(path)
for cl in myList :
    curimg = cv2.imread(f'{path}/{cl}')
    staff_img.append(curimg)
    staff_name.append(os.path.splitext(cl)[0])

def find_encoding(images) :
    imgEncodings = []
    for img in images :
        img = resize(img, 0.50)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodeimg = face_rec.face_encodings(img)[0]
        imgEncodings.append(encodeimg)
    return imgEncodings
def mark_attendance(name):
    now = datetime.now()
    timestr = now.strftime('%H:%M')
    #today = now.strftime("%m/%d/%Y")
    today = now.strftime("%d-%m-%Y")
    #{"$and": [{"name": name}, {"date": today}]}   
    if not mydb.attendance.count_documents({"$and": [{"name": name}, {"date": today}]}, limit = 1):
        mydict = { "name": name, "time": timestr, "date": today }
        x = mycol.insert_one(mydict)
        
        statment = str('entered' + name)
        engine.say(statment)
        engine.runAndWait()

EncodeList = find_encoding(staff_img)

vid = cv2.VideoCapture(0)
while True :
    success, frame = vid.read()
    Smaller_frames = cv2.resize(frame, (0,0), None, 0.25, 0.25)

    facesInFrame = face_rec.face_locations(Smaller_frames)
    encodeFacesInFrame = face_rec.face_encodings(Smaller_frames, facesInFrame)

    for encodeFace, faceloc in zip(encodeFacesInFrame, facesInFrame) :
        matches = face_rec.compare_faces(EncodeList, encodeFace)
        facedis = face_rec.face_distance(EncodeList, encodeFace)
        print(facedis)
        matchIndex = np.argmin(facedis)

        if matches[matchIndex] :
            name = staff_name[matchIndex].upper()
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.rectangle(frame, (x1, y2-25), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            mark_attendance(name)

    cv2.imshow('video',frame)
    cv2.waitKey(1)
