import mysql.connector

def camera_exist(mac):
    camera_exist = None
    try:
        connection = mysql.connector.connect(user='root', password='root',
                                             host='localhost',
                                             database='cameras',
                                             port='3306')

        cursor = connection.cursor()
        sql_select_query = """select * from camera where MAC = %s"""
        # set variable in query
        cursor.execute(sql_select_query, (mac,))
        if len(cursor.fetchall()) > 0:
            # fetch result
            record = cursor.fetchall()  # Recuperar todo
            camera_exist = True
            for row in record:
                print("MAC DE CAMARA: ", row[0], )
                print("UBICACION: ", row[1], "\n")
        else:
            camera_exist = False

    except mysql.connector.Error as error:
        print("Failed to get record from MySQL table: {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            return camera_exist

def get_camera_address(mac):
    record = None
    try:
        connection = mysql.connector.connect(user='root', password='root',
                                             host='localhost',
                                             database='cameras',
                                             port='3306')

        cursor = connection.cursor()
        sql_select_query = """select CameraAddress from camera where MAC = %s"""
        # set variable in query
        cursor.execute(sql_select_query, (mac,))
        record = cursor.fetchone()[0]  # Recuperar todo

    except mysql.connector.Error as error:
        print("Failed to get record from MySQL table: {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            return record
