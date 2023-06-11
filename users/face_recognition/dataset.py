import sys

import cv2
import os
import json
import os
DIRNAME = os.path.dirname(__file__)


def run(video, face_id, user_name):
    cam = cv2.VideoCapture(video)
    cam.set(3, 640)
    cam.set(4, 480)

    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")


    users_file_dict = {}
    with open(os.path.join(DIRNAME, 'users.json'), 'r') as f:
        users_file_dict = json.loads(f.read())
    print(users_file_dict)

    users_keys = list(users_file_dict.keys())
    users_values = list(users_file_dict.values())

    # if users_keys.__contains__(str(face_id)):
    #     print(json.dumps({"error": "ID exists"}))
    #     return

    users_file_dict[face_id] = user_name

    with open(os.path.join(DIRNAME, 'users.json'), "w") as file:
        file.write(json.dumps(users_file_dict))

    print("[INFO] Initializing face capture. Look the camera and wait ...")
    count = 0

    while (True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            count += 1

            cv2.imwrite(os.path.join(DIRNAME, "dataset/User." + str(face_id) + '.' + str(count) + ".jpg"), gray[y:y + h, x:x + w])
            cv2.imshow('image', img)

        k = cv2.waitKey(100) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break
        elif count >= 30:  # Take 30 face sample
            break

    print("[INFO] Successfully created user with\nid:{}\nname:{}".format(face_id, user_name))
    # Do a bit of cleanup
    print("[INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
    print(json.dumps({"result":"success"}))


if __name__ == '__main__':
    print("here")
    print(sys.argv)
    # face_id_input = input('[INFO] Enter user id and press <return> ==>  \n')
    # user_name_input = input('[INFO] Enter user name and press <return> ==>  \n')
    user_name = sys.argv[2]
    user_id = sys.argv[1]
    run(0, user_id, user_name)


