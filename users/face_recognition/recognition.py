import cv2
import numpy as np
import os
import json
def run():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('train/train.yml')
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);
    font = cv2.FONT_HERSHEY_SIMPLEX
    id = 0

    users_file_dict = {}
    with open('users.json', 'r') as f:
        users_file_dict = json.loads(f.read())

    print(users_file_dict)

    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)

    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    while True:
        ret, img =cam.read()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
           )

        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

            if (confidence < 100):
                # id = names[id]
                id = users_file_dict[str(id)]
                confidence = "  {0}%".format(round(100 - confidence))
                return id
            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)

        cv2.imshow('camera',img)
        k = cv2.waitKey(10) & 0xff #'ESC' for exite
        if k == 27:
            break

    print("[INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
