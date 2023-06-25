import cv2
import os
import face_recognition
import numpy as np
from PIL import Image
from Connection import camera_exist, get_camera_address
from datetime import datetime
from pathlib import Path
from Lectura_Imagenes import MAC_Camera
import uuid

path = 'static\personas_desaparecidas'  # Directorio
images = []  # Almacena las imagenes del directorio
classNames = []  # Almacena los nombres de las imagenes
myList = os.listdir(path)
encodeList = []

face_cascade = cv2.CascadeClassifier('cascades\data\haarcascade_frontalface_default.xml')
class VideoCamera(object):
    global encodeList

    def __init__(self):
        self.video = cv2.VideoCapture("https://192.168.100.94:8080/video")
        self.milliseconds = 0
        self.name = "No encontrado"
        self.formato_img = "jpg"

    def __del__(self):
        self.video.release()

    def get_frame(self):
        self.name = "No encontrado"
        ret, frame = self.video.read()
        roi_color = None
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray,1.3,5)
        for(x,y,w,h) in faces:
            roi_color = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),3)
        if self.milliseconds >= 50:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            facesCurFrame = face_recognition.face_locations(
                rgb_small_frame, )  # Enviamos la imagen a localizacion de rostro
            encodesCurFrame = face_recognition.face_encodings(rgb_small_frame,
                                                              facesCurFrame)
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeList, encodeFace, tolerance=0.59)  # Dejar en 45
                faceDis = face_recognition.face_distance(encodeList, encodeFace)
                print(faceDis)
                print(len(matches))
                matchIndex = np.argmin(faceDis)  # Obtenemos el valor menor (significa mayor similitud)
                if matches[matchIndex]:#and camera_exist(MAC_Camera())
                    self.name = classNames[matchIndex]  # Guardamos el nombre
                    if os.path.exists(f'static/personas_desaparecidas/{self.name}.jpg'):
                        img_detected_person = Image.open(f'static/personas_desaparecidas/{self.name}.jpg')
                        self.formato_img = "jpg"
                    elif os.path.exists(f'static/personas_desaparecidas/{self.name}.png'):
                        img_detected_person = Image.open(f'static/personas_desaparecidas/{self.name}.png')
                        self.formato_img = "png"
                    else:
                        img_detected_person = Image.open(f'static/personas_desaparecidas/{self.name}.jpeg')
                        self.formato_img = "jpeg"
                    print('TRUE')
                    print(self.name)

                    try:
                        cv2.imwrite(os.path.join('static/personas_encontradas', "2.png"), roi_color)
                        imagen = Image.open('static/personas_encontradas/2.png')
                        now = datetime.now()
                        horaObtenida = now.strftime("%Y-%m-%d_%Hhrs%Mmin%Sseg")

                        Path(f'static/personas_encontradas/{self.name}').mkdir(parents=True,
                                                                               exist_ok=True)  # Creamos una carpeta para la persona (en caso de no existir)
                        camera_address = ''
                        if camera_exist(MAC_Camera()):
                            camera_address = get_camera_address(MAC_Camera())
                        else:
                            print('Direccion no encontrada')
                        description = self.name + " " + camera_address + " " + horaObtenida + ".png"  # Guardamos la imagen
                        get_concat_h_resize(img_detected_person, imagen).save(
                            f'static/personas_encontradas/{self.name}/{description}')
                        image = cv2.imread(f'static/personas_encontradas/{self.name}/{description}')
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        org_name = (10, 130)
                        org_address = (10, 150)
                        fontScale = 0.5
                        color = (0, 0, 255)
                        thickness = 1

                        # image = cv2.putText(image, self.name, org_name, font,fontScale, color, thickness, cv2.LINE_AA)
                        # image = cv2.putText(image, camera_address, org_address, font, fontScale, color, thickness, cv2.LINE_AA)
                        cv2.imwrite(os.path.join(f'static/personas_encontradas/{self.name}/{description}', description),
                                    image)
                        # endregion
                        markAttendance(self.name, camera_address)  # Lo registramos en el csv
                    except:
                        print("No se pudo concatenar")
            self.milliseconds = 0
        else:
            self.milliseconds = self.milliseconds+1
        ret, jpeg = cv2.imencode('.jpg',frame)
        return jpeg.tobytes(), self.name, self.formato_img

    # region Almacenamiento de direcciones y nombres de las imagenes.
    def getImagesFromFolder(self):
        for cl in myList:  # Ciclo que itera por la cantidad de imagenes que se encuentren en el folder
            curImg = cv2.imread(f'{path}/{cl}')  # Direccion y nombre de la imagen
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])  # Agregamos el nombre de la imagen al arreglo
    # endregion

    # region Codificacion de imagenes de personas a encontrar
    def findEncodings(self):
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convertimos de BGR a RBG
            try:
                encode = face_recognition.face_encodings(img)[0]  # Codificamos el rostro que hemos detectado
                encodeList.append(encode)  # Lo agregamos al arreglo
            except:
                print(".")
        print(len(encodeList))
        print('Sistema listo...')
    # endregion

    # def images_saved_to_folder(frame):
    #     if os.path.exists(f'static/personas_desaparecidas/{name}.png'):
    #         img_detected_person = Image.open(f'static/personas_desaparecidas/{name}.png')
    #     elif os.path.exists(f'static/personas_desaparecidas/{name}.jpeg'):
    #         img_detected_person = Image.open(f'static/personas_desaparecidas/{name}.jpeg')
    #     elif os.path.exists(f'static/personas_desaparecidas/{name}.jpg'):
    #         img_detected_person = Image.open(f'static/personas_desaparecidas/{name}.jpg')
    #     else:
    #         print("Concatenando imagenes...")
    #         return False
    #     now = datetime.now()
    #     date_string = now.strftime("%Y-%m-%d_%Hhrs%Mmin%Sseg")
    #     # description = name + " " + date_string + " " + camera_address + ".png"  # Guardamos la imagen
    #     description = name + ".png"  # Guardamos la imagen
    #     # PROBLEMA CON EL FRAME, POSIBLEMENTE NO SEA POSIBLE GUARDARLO COMO IMAGEN Y CONCATENARLO------------------
    #     get_concat_h_resize(img_detected_person, frame).save(f'personas_encontradas/{name}/{description}')
    #     return True

def get_concat_h_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
    if im1.height == im2.height:
        _im1 = im1
        _im2 = im2
    elif (((im1.height > im2.height) and resize_big_image) or
          ((im1.height < im2.height) and not resize_big_image)):
        _im1 = im1.resize((int(im1.width * im2.height / im1.height), im2.height), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((int(im2.width * im1.height / im2.height), im1.height), resample=resample)
    dst = Image.new('RGB', (_im1.width + _im2.width, _im1.height))
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (_im1.width, 0))
    return dst

#
# def MAC_Camera():
#     mac_camera = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
#                            for ele in range(0, 8 * 6, 8)][::-1])
#     return mac_camera

# region Registro de persona reconocida
def markAttendance(name, camera_address):  # Escribe el nombre una vez que sea reconocido
    with open('Registros_encontradas.csv', 'r+') as f:  # Abrimos el archivo
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')  # Agregamos el separador
            nameList.append(entry[0])  # Agregamos el nombre a la lista
        if name not in nameList:
            now = datetime.now()
            time_string = now.strftime('%H:%M:%S')
            date_string = now.strftime('%Y-%m-%d')
            f.writelines(f'\n{name},{camera_address},{time_string},{date_string}')
        elif name not in nameList[len(nameList) - 1]:  # Si existe en la lista y no es el ultimo
            now = datetime.now()
            time_string = now.strftime('%H:%M:%S')
            date_string = now.strftime('%Y-%m-%d')
            f.writelines(f'\n{name},{camera_address},{time_string},{date_string}')