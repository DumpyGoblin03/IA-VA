from flask import Flask, render_template, Response
from camera import VideoCamera
import os
from datetime import datetime
import pyautogui
import uuid
from Connection import camera_exist
from Connection import get_camera_address

encoded = False
app = Flask(__name__)
img = os.path.join('static', 'Image')
name = "No encontrado"
formato_img = "jpg"
horaObtenida = ""
fechaObtenida = ""
path = ''
camera_address = ''
flag = True


@app.route('/')
def index():
    return render_template('index.html', img_name=name, HO=horaObtenida, FO=fechaObtenida, PATH=path, CA= camera_address, UO=camera_address, FI=formato_img)


def gen(camera):
    global name
    global encoded
    global horaObtenida
    global fechaObtenida
    global path
    global camera_address
    global flag
    global formato_img
    path = ''
    if not encoded:
        camera.getImagesFromFolder()
        camera.findEncodings()
        encoded = True
    while True:
        frame, name, formato_img = camera.get_frame()
        if name == "No encontrado" and flag:
            path = ''
            flag = False
            pyautogui.hotkey('f5')
        elif name != "No encontrado":
            now = datetime.now()
            horaObtenida = now.strftime("%H:%M:%S")
            fechaObtenida = now.strftime("%d-%m-%Y")
            path = 'personas_desaparecidas/'
            if camera_exist(MAC_Camera()):
                camera_address = get_camera_address(MAC_Camera())
            else:
                print('Direccion no encontrada')
            #images_saved_to_folder(frame)
            pyautogui.hotkey('f5')
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame +
               b'\r\n\r\n')


def MAC_Camera():
    mac_camera = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                           for ele in range(0, 8 * 6, 8)][::-1])
    return mac_camera
# endregion


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
