import cv2
import numpy as np
import os
import json
from collections import Counter

DIRNAME = os.path.dirname(__file__)


def run(video):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(os.path.join(DIRNAME, './train/train.yml'))
    cascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)
    font = cv2.FONT_HERSHEY_SIMPLEX
    id = 0

    users_file_dict = {}
    with open(os.path.join(DIRNAME, 'users.json'), 'r') as f:
        users_file_dict = json.loads(f.read())

    # print(users_file_dict)

    cam = cv2.VideoCapture(video)
    cam.set(3, 640)
    cam.set(4, 480)

    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    user_counter = Counter()
    for index in range(90):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            percent = round(100 - confidence)
            if (percent > 50):
                # id = names[id]
                name = users_file_dict[str(id)]
                user_counter[id] += 1
            # confidence = "  {0}%".format(round(100 - confidence))
            else:
                id = 0
                name = "unknown"
                user_counter[id] += 1
            # confidence = "  {0}%".format(round(100 - confidence))
            cv2.putText(img, name, (x + 5, y - 5), font, 1, (255, 255, 255), 2)

        cv2.imshow('camera', img)
        cv2.moveWindow('camera', 600, 250)
        k = cv2.waitKey(10) & 0xff  # 'ESC' for exite
        if k == 27:
            break
    #	if index % 10 == 0:
    #		print("in cycle", index)

    # print("[INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
    _, max_id = max([(value, key) for key, value in user_counter.items()], default=(0, 0))
    if max_id == 0:
        print(json.dumps({"error": "cannot recognize"}))
    else:
        print(json.dumps({"result": [str(max_id), users_file_dict[str(max_id)]]}))
        # print("here",max_id, "22")
    return user_counter


if __name__ == '__main__':
    run(0)