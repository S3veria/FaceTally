"""
Project Name Here - Written by Santiago Reyes

This application is made specifically for companies looking to improve their clocking in/out flow.
Using OpenCv I was able to create an app that allows employes to clock in and out with extreame ease.
Simply by walking up to where the camera is pointed, any registered employee will be detected using face recognition.
Once an employee has been found, a GUI will be displayed; here, the employee will be greeted and be able to clock in and out.
Logic was also implemented to prevent employees from clocking in multiple times in a row or clocking out in the same way.

Once the action is complete, the information will be saved and stored
in csv file named after the current date inside that months folder.
This should provide any higher up to visualize every days data (clocking times, names, total work time, entries and exits)

"""

#First we import all the libraries we will be using for this project
import cv2
import numpy as np
import face_recognition
import os
import tkinter as tk
from tkinter import *
import csv
from PIL import Image,ImageTk
from tkinter.font import Font
from tkinter import messagebox
import datetime

#We initialize some of the important variables that will be used late on in the program
images=[]
classNames=[]
myList=os.listdir("Images Basic")
monthNames=["January", "February","March", "April","May", "June","July", "August","September", "October","November", "December"]
#We save previous name as an empty string; this will change its value to whoever was detected last to prevent
#detecting the person multiple times in a row
prevName=""

#A for loop is used to find all the images (employees) and add them to a list
for cls in myList:
    curImg=cv2.imread(f'Images Basic/{cls}')
    images.append(curImg)
    classNames.append(os.path.splitext(cls)[0])

#This function will be called whenever an employee has been recognized
def confirmedID(employeeName, d):
    #We make use of the datetime library to find and write files depending on the current date
    now = datetime.now()
    curr_time = now.strftime("%H:%M:%S")
    day=now.day
    month=now.month
    year=now.year
    docTitle=f'{day}-{month}-{year}'
    entries=0
    #We create a path for the folder that our file should be located in
    folderTitle = f'\{monthNames[int(month)-1]}-{year}'
    parent = os.getcwd()
    folderPath = parent + folderTitle
    #Tries to access the csv document
    try:
        with open(os.path.join(folderPath,f"{docTitle}.csv"), "r") as f:
            print("File for this day has been found")
            reader = csv.reader(f)
            for line in reader:
                for attribute in line:
                    if attribute == employeeName:
                        entries+=1
        if entries==0 or entries%2==0:
            with open(os.path.join(folderPath,f"{docTitle}.csv"), "a", newline='') as f:
                headers = ['EMPLOYEE', 'TIME', 'ACTION', 'TOTAL WORK']
                writer = csv.DictWriter(f, headers)
                writer.writerow({'EMPLOYEE': employeeName, 'TIME': curr_time, 'ACTION': "Entry",'TOTAL WORK': "---"})
                d.destroy()
        else:
            print("That employee is already signed in")
            messagebox.showerror("Already signed in!",
                                 "Sorry, there is already an entry log for you today...")
    #If the try fails, it means that the file does not exist and must be created
    except:
        #Now we check if the folder exists, if it doesnt, it is created
        if not os.path.isdir(folderPath):
            os.mkdir(folderPath)
        #And now we actually write the csv file
        with open(os.path.join(folderPath,f"{docTitle}.csv"), "w", newline='') as f:
            headers = ['EMPLOYEE', 'TIME', 'ACTION', 'TOTAL WORK']
            writer = csv.DictWriter(f, headers)
            writer.writeheader()
            writer.writerow({'EMPLOYEE': employeeName, 'TIME': curr_time, 'ACTION': "Entry",'TOTAL WORK': "---"})
            #The GUI is destroyed so it can be recreated with other attributes
            d.destroy()

#This function is callen whenever an employee clocks out
def exitLog(employeeName,wind):
    now = datetime.now()
    curr_time = now.strftime("%H:%M:%S")
    h=now.hour
    m=now.minute
    s=now.second
    day=now.day
    month=now.month
    year=now.year
    docTitle = f'{day}-{month}-{year}'
    total = 0
    listedTimes = []
    giveWarning=True
    folderTitle = f'\{monthNames[int(month)-1]}-{year}'
    parent = os.getcwd()
    cosa = parent + folderTitle
    #We check that the employee has clocked in previously
    try:
        with open(os.path.join(cosa, f"{docTitle}.csv"), "r") as f:
            reader = csv.reader(f)
            for line in reader:
                for attribute in line:
                    if attribute == employeeName:
                        #We save the time that the employee came in at so we can calculate the total time worked
                        total += 1
                        time = line[1].split(":")
                        listedTimes.append(time)
                        print(time)
        print(total)
    except:
        print("You cant log out, there is no log for this day")
        messagebox.showerror("Unable to create exit log!",
                             "Sorry, there is no log file for today, please log in to create it")
        giveWarning=False

    if(total!=0 and (total%2)!=0):
        #Calculate total time worked
        print(listedTimes)
        hours = int(h)-int(listedTimes[-1][0])
        minutes = int(m)-int(listedTimes[-1][1])
        seconds =int(s)-int(listedTimes[-1][2])
        print(hours,minutes,seconds)
        if seconds < 0:
            minutes -= 1
            seconds += 60
        if minutes < 0:
            hours -= 1
            minutes += 60

        #We append the new information to the csv file
        with open(os.path.join(cosa,f"{docTitle}.csv"), "a", newline='') as f:
            headers = ['EMPLOYEE', 'TIME', 'ACTION', 'TOTAL WORK']
            writer = csv.DictWriter(f, headers)
            hText=f'{hours}'
            if hours<10:
                hText = f'0{hours}'
            mText=f'{minutes}'
            if minutes<10:
                mText = f'0{minutes}'
            sText=f'{seconds}'
            if seconds<10:
                sText = f'0{seconds}'
            timeText=f'{hText}:{mText}:{sText}'
            writer.writerow({'EMPLOYEE': employeeName, 'TIME': curr_time, 'ACTION': "Exit", 'TOTAL WORK': timeText})
        wind.destroy()
    else:
        if giveWarning:
            print("You cant log out if you have not logged in")
            messagebox.showerror("No entry log!", "Sorry, you can not exit at this moment because there is no entry logged for you")


#This is the GUI window created with Tkinter
def mainWindow(nam):
    #Icons for the following buttons were retrieved from:
    #Entry Exit by Akshar Pathak from the Noun Project


    root = tk.Tk()
    titleFont = Font(family="Rockwell", size="25", weight="bold")
    root.geometry('500x500')
    root.title("Facial recognition autoclocker")
    root.configure(bg="#E6E3DB")
    bannerC = tk.Label(root, bg="#BC997C", width=500, height=3)
    bannerC.pack()
    entryImg = Image.open('Assets\entry.png')
    entryImg = entryImg.resize((123, 51), Image.ANTIALIAS)
    entry = ImageTk.PhotoImage(entryImg)
    entryBtn = tk.Button(root, image=entry, borderwidth=0, bg="#E6E3DB", activebackground="#E6E3DB",command=lambda:confirmedID(nam,root))
    entryBtn.image = entry
    entryBtn.place(anchor=CENTER, relx=0.25, rely=0.825)

    exitImg = Image.open('Assets\exit.png')
    exitImg = exitImg.resize((123, 51), Image.ANTIALIAS)
    exit = ImageTk.PhotoImage(exitImg)
    exitBtn = tk.Button(root, image=exit, borderwidth=0, bg="#E6E3DB", activebackground="#E6E3DB",command=lambda:exitLog(nam,root))
    exitBtn.image = exit
    exitBtn.place(anchor=CENTER, relx=0.75, rely=0.825)

    greeting = tk.Label(root, text=f"Welcome, {nam}", fg="#000000", bg="#BC997C", font=titleFont)

    greeting.place(anchor=CENTER, relx=0.5, rely=0.05)

    mainImage = Image.open('Assets\imagen.png')
    mainImage = mainImage.resize((426, 320), Image.ANTIALIAS)
    tkImage = ImageTk.PhotoImage(mainImage)
    labelImg = tk.Label(image=tkImage, borderwidth=0)
    labelImg.image = tkImage
    labelImg.place(anchor=N, relx=0.5, rely=0.125)
    root.mainloop()


#This function encodes the images we loaded in the beggining
def findEncodings(imagenes):
    encoded=[]
    for imagen in imagenes:
        imagen=cv2.cvtColor(imagen,cv2.COLOR_BGR2RGB)
        enc = face_recognition.face_encodings(imagen)[0]
        encoded.append(enc)
    return encoded

#We use the function explained previously
encodedImages=findEncodings(images)
#We use OpenCv to get video input
cap=cv2.VideoCapture(0)

#This is the actual face recognition part of the code
while True:
    success, img=cap.read() #We read the video input
    imgS=cv2.resize(img,(0,0),None,0.25,0.25) #Resizing for memomory/time efficiency

    #We format the input and find the face encondings
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(imgS)
    encodedWebCam = face_recognition.face_encodings(imgS,faces)

    #We use this for loop to compare and find the best match beween the encoded video and the encoded images we preloaded
    for encF,loc in zip(encodedWebCam,faces):
        best = 1
        pos = 0
        matches = face_recognition.compare_faces(encodedImages, (encF))
        distance=face_recognition.face_distance(encodedImages, (encF))
        inde=np.argmin(distance)
        print(distance[inde])
        if matches[inde]:
            #If there is not a good enough match, the face will be recognized as "UNKNOWN"
            if distance[inde]>=0.48:
                name="UNKNOWN"
            else:
                name=classNames[inde].upper()


            #Finally, we simply restablish the original size of the video capture
            #We also insert the visual atributes: the red box and the name
            y1, x2, y2, x1 = loc
            y1, x2, y2, x1=y1*4, x2*4, y2*4, x1*4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),1)
        # This part of the code is comented out because it is not necesary for the app to run properly
        # The purpose of this code is to visualize the face detection being applied, if you wish to see it simply uncomment this section
        cv2.imshow('Face Recognition Display', img)
        cv2.waitKey(1)

        if (prevName != name) & (name!="UNKNOWN"):
            print("Aqui guarda esta cosa")
            cv2.imwrite("Assets/imagen.png", img)
            mainWindow(name)
            prevName=name
