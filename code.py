
import tkinter as tk
from tkinter import Message ,Text
import cv2,os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font

window = tk.Tk()
window.title("Face_Recogniser")

dialog_title = 'QUIT'
dialog_text = 'Do you really want to quit?'

window.configure(background='white')


window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)



message = tk.Label(window, text="Attendance management" ,bg="midnight blue"  ,fg="white"  ,width=42  ,height=3,font=('Courier', 30, 'italic bold underline')) 

message.place(x=180, y=15)

lbl = tk.Label(window, text="Enter ID",width=20  ,height=2  ,fg="white"  ,bg="dark slate gray" ,font=('Courier', 15, ' bold ') ) 
lbl.place(x=400, y=200)

txt = tk.Entry(window,width=20   ,bg="powder blue" ,fg="black",font=('Courier', 15, ' bold '))
txt.place(x=700, y=215)

lbl2 = tk.Label(window, text="Enter Name",width=20  ,fg="white"  ,bg="dark slate gray"    ,height=2 ,font=('Courier', 15, ' bold ')) 
lbl2.place(x=400, y=300)

txt2 = tk.Entry(window,width=20  ,bg="powder blue"  ,fg="black",font=('Courier', 15, ' bold ')  )
txt2.place(x=700, y=315)

lbl3 = tk.Label(window, text="Action : ",width=20  ,fg="white"  ,bg="dark slate gray"  ,height=2 ,font=('Courier', 15, ' bold underline ')) 
lbl3.place(x=400, y=400)

message = tk.Label(window, text="" ,bg="powder blue"  ,fg="black"  ,width=50  ,height=2, activebackground = "dark slate gray" ,font=('Courier', 15, ' bold ')) 
message.place(x=700, y=400)

lbl3 = tk.Label(window, text="Attendance : ",width=20  ,fg="white"  ,bg="dark slate gray"  ,height=2 ,font=('Courier', 15, ' bold  underline')) 
lbl3.place(x=400, y=650)


message2 = tk.Label(window, text="" ,fg="black"   ,bg="powder blue",activeforeground = "dark slate gray",width=40  ,height=4  ,font=('Courier', 15, ' bold ')) 
message2.place(x=660, y=625)

    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False
 
def TakeImages():        
    Id=(txt.get())
    name=(txt2.get())
    if(is_number(Id) and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haar_features.xml"
        detector=cv2.CascadeClassifier(harcascadePath)
        sampleNum=0
        while(True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)        

                sampleNum=sampleNum+1

                cv2.imwrite("Train_image\ "+name +"."+Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])

                cv2.imshow('frame',img)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum>100:
                break
        cam.release()
        cv2.destroyAllWindows() 
        res = "Images Saved for ID : " + Id +" Name : "+ name
        row = [Id , name]
        with open('Student_File\Student_File.csv','a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message.configure(text= res)
    else:
        if(is_number(Id)):
            res = "Your Id is not Numeric: please try again"
            message.configure(text= res)
        if(name.isalpha()):
            res = "Your name is not Alphabatic: please try again"
            message.configure(text= res)
    
def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    harcascadePath = "haar_features.xml"
    detector =cv2.CascadeClassifier(harcascadePath)
    faces,Id = getImagesAndLabels("Train_image")
    recognizer.train(faces, np.array(Id))
    recognizer.save("Train_imageLabel\Trainner.yml")
    res = "Image Has Trained"
    message.configure(text= res)

def getImagesAndLabels(path):
    
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 

    
    #creating the empty face list
    faces=[]
    #creating the empty ID list
    Ids=[]
    
    for imagePath in imagePaths:
        
        pilImage=Image.open(imagePath).convert('L')
        
        imageNp=np.array(pilImage,'uint8')
       
        Id=int(os.path.split(imagePath)[-1].split(".")[1])
        
        faces.append(imageNp)
        Ids.append(Id)        
    return faces,Ids

def TrackImages():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("Train_imageLabel\Trainner.yml")
    harcascadePath = "haar_features.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);    
    df=pd.read_csv("Student_File\Student_File.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX        
    col_names =  ['Id','Name','Date','Time']
    attendance = pd.DataFrame(columns = col_names)    
    while True:
        ret, im =cam.read()
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray, 1.2,5)    
        for(x,y,w,h) in faces:
            cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
            Id, conf = recognizer.predict(gray[y:y+h,x:x+w])                                   
            if(conf < 50):
                ts = time.time()      
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa=df.loc[df['Id'] == Id]['Name'].values
                tt=str(Id)+"-"+aa
                attendance.loc[len(attendance)] = [Id,aa,date,timeStamp]
            else:
                Id="You don't belong to this class"                
                tt=str(Id)  
            if(conf > 75):
                noOfFile=len(os.listdir("ImagesUnknown"))+1
                cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])            
            cv2.putText(im,str(tt),(x,y+h), font, 1,(255,255,255),2)        
        attendance=attendance.drop_duplicates(subset=['Id'],keep='first')    
        cv2.imshow('im',im) 
        if (cv2.waitKey(1)==ord('q')):
            break
    ts = time.time()      
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour,Minute,Second=timeStamp.split(":")
    fileName="Attendance\Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
    attendance.to_csv(fileName,index=False)
    cam.release()
    cv2.destroyAllWindows()
    res=attendance
    message2.configure(text= res)

     
takeImg = tk.Button(window, text="Feed Images Data", command=TakeImages  ,fg="white"  ,bg="dark slate gray"  ,width=20  ,height=3, activebackground = "white" ,font=('Courier', 15, ' bold '))
takeImg.place(x=200, y=500)
trainImg = tk.Button(window, text="Train Images", command=TrainImages  ,fg="white"  ,bg="dark slate gray"  ,width=20  ,height=3, activebackground = "white" ,font=('Courier', 15, ' bold '))
trainImg.place(x=500, y=500)
trackImg = tk.Button(window, text="Take Attendance", command=TrackImages  ,fg="white"  ,bg="dark slate gray"  ,width=20  ,height=3, activebackground = "white" ,font=('Courier', 15, ' bold '))
trackImg.place(x=800, y=500)
quitWindow = tk.Button(window, text="Quit", command=window.destroy  ,fg="white"  ,bg="dark slate gray"  ,width=20  ,height=3, activebackground = "white" ,font=('Courier', 15, ' bold '))
quitWindow.place(x=1100, y=500) 
window.mainloop()