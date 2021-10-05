import socket
import time
import hashlib
import struct as st
from os import path
import threading
import logging

numClientes = int(input('Ingrese el numero de clientes que desea crear>> '))

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
)

def clientFunction(name):
    PORT = 9005
    FORMAT = 'utf-8'
    SERVER = "192.168.231.128"
    ADDR = (SERVER, PORT)
    FILES_DIR = 'archivos'
    LOGS_DIR = 'logs'
    
    
    abs_path = path.dirname(path.abspath(__file__))
    files_path = path.join(abs_path,FILES_DIR)
    logs_path = path.join(abs_path,LOGS_DIR)
    
    def obtener_hash(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        f.close()
        return hash_md5.digest()
    
    # Se crea el socket
    s = socket.socket()
    s.connect(ADDR)
    # Se crea el log
    file_name = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())+'-log'+str(name)+'.txt'
    log = open(path.join(logs_path, file_name),'w')
    
    # Recibe si el server esta listo
    console_msg = str(s.recv(255).decode(FORMAT))
    logging.info(console_msg)

    
    # Saluda al cliente
    s.send("Ready".encode(FORMAT))
    
    # Se registra el nombre del archivo
    file_name = str(s.recv(255).decode(FORMAT))
    log.write('Se recibe el archivo {} \n'.format(file_name))
    
    
    file_name = "Cliente"+str(name)+"-Prueba-"+str(numClientes)+".txt"
    file_path = path.join(files_path,file_name)
    
    # Se extrae el archivo y se determina su peso
    with open(file_path, 'wb') as f:
        # Se recibe el tamaño del archivo
        file_size = int(st.unpack('I',s.recv(4))[0])
        log.write('El archivo pesa {} bytes\n'.format(file_size))
    
        # Se guarda el archivo en el cliente    
        total_file_size = 0
        while total_file_size < file_size:
            data = s.recv(10*1024)
            total_file_size+=len(data)
            f.write(data)
        f.close()
        
    s.send('Archivo recibido'.encode(FORMAT))
    # Se recibe el hash del server
    checksum = s.recv(64)
    checksum_local = obtener_hash(file_path)
    
    # Se determina si el archivo llego correctamente o no
    if checksum == checksum_local:
        s.send("ok".encode(FORMAT))
        console_msg = 'El archivo de '+str(file_size)+" bytes se recibio de forma exitosa"
        log.write(console_msg+'\n')
        logging.info(console_msg)
    else:
        s.send("not ok".encode(FORMAT))
        console_msg = 'El archivo no se recibio bien'
        log.write(console_msg+'\n')
        logging.info(console_msg)
        
    
    # Se envia el tiempo de terminacion
    s.send(st.pack('d',time.time()))
    
    # Se recibe el tiempo total
    total_time = float(st.unpack('d',s.recv(8))[0])
    log.write('Tiempo de transmicion fue: {} s \n'.format(round(total_time,3) ))
    log.write(console_msg+'\n')
    logging.info(console_msg)
    
    # Se cierra todo
    s.close()
    console_msg = 'Se cierra la conexion'
    logging.info(console_msg)
    log.close()
    
    
    
clientes = []
for i in range(numClientes):
    t = threading.Thread(name='Cliente'+str(i), target=clientFunction, args=(i,))
    clientes.append(t)
    t.start()