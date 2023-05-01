import subprocess

subprocess.run([f"python3 users/face_recognition/dataset.py 1 alex_smith"], shell=True, capture_output=True)
