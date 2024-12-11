
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 10:48:27 2024

@author: tqk2811
"""

import cv2
import csv
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import pandas as pd
import face_recognition
import threading
import time

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
filename = "database/dataWriteTest.csv"

ef = pd.read_csv(filename)
empno = ef["Employee ID"].tolist()
firstname = ef["Full Name"].tolist()
photolocation = ef["Picture Address"].tolist()
n = len(empno)
emp = []
emp_encod = []
audio = []
regEmp = "..."

# faceIndex = None

running = True

# Hàm để chạy face_recog() mỗi giây
def run_face_recog():
    global running
    while running:
        face_recog()
        time.sleep(2)

def capture_images():
    ret, frame = cap.read()
    for i in range(10):
        cv2.imwrite('Employee'+str(i)+'.png', frame)
    
# def run_face_recog_thread():
#     check_thread = threading.Thread(target=face_recog)
#     check_thread.start()
    
def run_face_recog_thread():
    def loop_recognition():
        while running:  # `running` là một biến toàn cục để kiểm soát việc dừng luồng
            face_recog()  # Gọi hàm nhận diện khuôn mặt
            time.sleep(1)  # Chờ 5 giây trước khi lặp lại
            
    global running
    running = True

    # Tạo luồng mới để thực hiện vòng lặp nhận diện khuôn mặt
    check_thread = threading.Thread(target=loop_recognition)
    check_thread.start()

def face_recog():
    global regEmp
    emp.clear()
    emp_encod.clear()
    for i in range(n):
        emp.append(face_recognition.load_image_file(photolocation[i]))
        emp_encod.append(face_recognition.face_encodings(emp[i])[0])
        
    capture_thread = threading.Thread(target=capture_images, args=())
    capture_thread.start()
    uk =face_recognition.load_image_file('Employee5.png')
    emp_index = identify_employee(uk)    
    if emp_index != -1:
        result_text = f"{emp_index} : id- {empno[emp_index]} / {firstname[emp_index]}"
        regEmp = f"{firstname[emp_index]}"
    else:
        result_text = "Employee not recognized"
        regEmp = "unknown..."
    print(regEmp)
    # Update the Label text
    result_label.config(text=result_text)
    
# Function to capture an image using the webcam
def take_picture():
    global cap, img_label
    
    # Capture a frame from the webcam
    ret, frame = cap.read()
    
    if ret:
        save_dir = "./faceImgPrj/"
        
        # Find the next available filename
        i = 1
        while os.path.exists(f"{save_dir}picture{i}.jpg"):
            i += 1
        
        # Save the image with the next available filename
        save_path = f"{save_dir}picture{i}.jpg"
        cv2.imwrite(save_path, frame)
        
        # Show a confirmation message
        messagebox.showinfo("Success", f"Picture saved to {save_path}")
    else:
        messagebox.showerror("Error", "Failed to capture image")
    return save_path

# Function to update the camera feed in the window
def update_frame():
    global cap, img_label
    
    ret, frame = cap.read()
    if ret:
        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Draw bounding boxes around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # text = "linh?"
            cv2.putText(frame, regEmp, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Convert the frame to RGB (Tkinter uses RGB images)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Update the image in the label
        img_label.imgtk = imgtk
        img_label.configure(image=imgtk)
    
    # Call update_frame again after 10ms
    img_label.after(10, update_frame)
    
def append_data():
    empid = id_entry.get().strip()
    name = name_entry.get().strip()

    if not name or not empid:
        messagebox.showwarning("Warning", "All fields must be filled out.")
        return
    
    # Append the data to the CSV file
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([empid, name, take_picture()])
    
    messagebox.showinfo("Success", f"Data saved: {empid}, {name}")
    # Clear the fields after saving
    id_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    
def take_pic_and_insert():
    append_data()
    
def identify_employee(photo):
    uk_encodings = face_recognition.face_encodings(photo)
    print(photo)
    print("-----------------------------------------------")
    print(uk_encodings)

    if not len(uk_encodings) > 0:
        print("No face found in the provided photo.")
        result_text = "No face found in the provided photo."
        result_label.config(text=result_text)
        return -1  # Return None if no face is found

    uk_encode = uk_encodings[0]
    found = face_recognition.compare_faces(
                emp_encod, uk_encode, tolerance = 0.4)    
    print(found)
    
    index = -1
    for i in range(n):
        if found[i]:
            index = i
    return(index)

def stop_recognition():
    global running
    running = False

# Set up the GUI
root = tk.Tk()
root.title("Capture Image")

# Initialize webcam
cap = cv2.VideoCapture(0)

# Create a label to show the camera feed
img_label = tk.Label(root)
img_label.pack()

result_label = tk.Label(root, text="", font=("Helvetica", 14))
result_label.pack()

check_btn = tk.Button(root, text="Check in", command=run_face_recog_thread)
check_btn.pack(side=tk.RIGHT)

stop_btn = tk.Button(root, text="Stop Recognition", command=stop_recognition)
stop_btn.pack(side=tk.RIGHT)

# Create a frame to organize the input fields
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

# Employee ID input
tk.Label(input_frame, text="Employee ID:").grid(row=0, column=0, padx=5, pady=5)
id_entry = tk.Entry(input_frame)
id_entry.grid(row=0, column=1, padx=5, pady=5)

# Name input
tk.Label(input_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5)
name_entry = tk.Entry(input_frame)
name_entry.grid(row=1, column=1, padx=5, pady=5)

# Create a button that triggers the append_data function
confirm_btn = tk.Button(root, text="Confirm", command=take_pic_and_insert)
confirm_btn.pack(pady=20)

# Start updating the camera feed
update_frame()

# Start the GUI event loop
root.mainloop()

# Release the camera when closing the app
cap.release()
cv2.destroyAllWindows()
