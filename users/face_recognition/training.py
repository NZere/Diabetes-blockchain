import cv2
import numpy as np
from PIL import Image
import os
DIRNAME = os.path.dirname(__file__)

path = 'dataset'
recognizer = cv2.face.LBPHFaceRecognizer_create()
cascade = cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")


def get_images_and_labels(path):
    img_paths = [os.path.join(path, f) for f in os.listdir(path)]
    face_samples = []
    ids = []

    for imgPath in img_paths:
        PIL_img = Image.open(imgPath).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')
        id = int(os.path.split(imgPath)[-1].split(".")[1])
        faces = cascade.detectMultiScale(img_numpy)

        for (x, y, w, h) in faces:
            face_samples.append(img_numpy[y:y + h, x:x + w])
            ids.append(id)
    return face_samples, ids


def run():
    print("[INFO] Training faces. It will take a few seconds. Wait ...")
    faces, ids = get_images_and_labels(os.path.join(DIRNAME, path))
    recognizer.train(faces, np.array(ids))
    recognizer.write(os.path.join(DIRNAME, './train/train.yml'))
    print("[INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))


if __name__ == '__main__':
    run()

