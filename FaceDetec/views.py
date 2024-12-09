from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from datetime import datetime
import cv2
import os
import mediapipe as mp
import numpy as np
from .forms import UserForm
from .models import Attendance
import face_recognition

# Inisialisasi face detector
face_cascade = cv2.CascadeClassifier('faceDetec.xml')

# Inisialisasi Mediapipe untuk deteksi landmark wajah
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Direktori untuk menyimpan wajah
output_dir = "saved_faces"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def home(request):
    new_entry = None  # Untuk menyimpan data terbaru yang dimasukkan

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            new_entry = form.save()
            return redirect('scan_face')
    else:
        form = UserForm()

    # Ambil semua data absensi
    attendance_data = Attendance.objects.all()

    return render(request, 'home.html', {
        'form': form,
        'attendance_data': attendance_data,
        'new_entry': new_entry,  
    })

def detec(request):
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
    cap = cv2.VideoCapture(0)
    teeth_visible_status = False

    # Ambil data pengguna terakhir yang disimpan
    user = Attendance.objects.last()
    name = user.name if user else "Unknown"
    age = user.age if user else 0

    face_saved_count = 0
    max_faces_to_save = 5

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Konversi ke RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        # Deteksi landmark wajah
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=False,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style(),
                )

                # Landmark mulut
                mouth = [face_landmarks.landmark[i] for i in [13, 14]] 

                # Hitung jarak
                def calculate_distance(point1, point2):
                    return ((point1.x - point2.x)**2 + (point1.y - point2.y)**2) ** 0.5

                mouth_open = calculate_distance(mouth[0], mouth[1]) > 0.03
                teeth_visible_status = mouth_open

                # Menampilkan nama dan umur pengguna di atas kepala
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, f"Name: {name}", (10, 30), font, 0.8, (0, 0, 255), 2)
                cv2.putText(frame, f"Age: {age}", (10, 60), font, 0.8, (0, 0, 255), 2)

                # Menampilkan status verifikasi mulut terbuka
                teeth_status_text = "Buka mulut untuk verifikasi!"
                cv2.putText(frame, teeth_status_text, (10, 120), font, 0.5, (17, 255, 255), 2)

                if teeth_visible_status:
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                    for (x, y, w, h) in faces:
                        # Crop wajah dari frame
                        face_img = frame[y:y+h, x:x+w]

                        # Simpan wajah ke folder
                        if face_saved_count < max_faces_to_save:
                            safe_name = ''.join(char if char.isalnum() or char in "_-" else '_' for char in name)
                            face_path = os.path.join(output_dir, f"face_{safe_name}_{face_saved_count}.png")
                            try:
                                cv2.imwrite(face_path, face_img)
                                print(f"Wajah disimpan: {face_path}")
                                face_saved_count += 1
                            except Exception as e:
                                print(f"Error menyimpan wajah: {e}")

                        if face_saved_count >= max_faces_to_save:
                            print("Jumlah maksimum wajah telah disimpan.")
                            cap.release()
                            cv2.destroyAllWindows()
                            return redirect('input_data')

        # Menampilkan frame di layar
        cv2.imshow('Face Absen', frame)

        # Tekan 'q' untuk keluar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return JsonResponse({'status': 'scan interrupted'})
