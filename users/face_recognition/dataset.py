import cv2
import os
import json


def run():
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)

    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    face_id = None
    user_name = None

    users_file_dict = {}
    with open('users.json', 'r') as f:
        users_file_dict = json.loads(f.read())
    print(users_file_dict)

    users_keys = list(users_file_dict.keys())
    users_values = list(users_file_dict.values())
    while face_id is None:
        face_id_input = input('[INFO] Enter user id and press <return> ==>  \n')
        if users_keys.__contains__(str(face_id_input)):
            print('[INFO] ID EXISTS!!! try again')
            face_id = None
        else:
            ok = True
            face_id = face_id_input

    while user_name is None:
        user_name_input = input('[INFO] Enter user name and press <return> ==>  \n')
        if users_values.__contains__(str(user_name_input)):
            print('[INFO] NAME EXISTS!!! try again')
            user_name = None
        else:
            ok = True
            user_name = user_name_input

    users_file_dict[face_id] = user_name


    with open("users.json", "w") as file:
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

            cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])
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
