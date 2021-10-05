import socket
import threading
from os import path, listdir
import time
import hashlib
import struct as st

PORT = 9000
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
FILES_DIR = 'archivos'
LOGS_DIR = 'logs'

all_conns = []
abs_path = path.dirname(path.abspath(__file__))
files_path = path.join(abs_path,FILES_DIR)
logs_path = path.join(abs_path,LOGS_DIR)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def obtener_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    f.close()
    return hash_md5.digest()


# Elige que archivo se va a enviar y a cuantos clientes se va a esperar
def iniciar_server():
    try:
        global file_path
        global file_name
        global file_size
        global hash_local
        global num_usuarios
        
        
        del all_conns[:]
        global num_usuarios
        num_usuarios = int(input('Numero de usuarios a enviar>> '))
        
        files = ['100.txt', '250.txt']
        file_name = files[int(input('Ingrese el archivo que desea usar (1 para 100Mb) (2 para 250Mb)>> '))]
        file_path = path.join(files_path,file_name)
        file_size = path.getsize(file_path)
        hash_local = obtener_hash(file_path)
    
    except Exception as e :
        print('Ocurrio un error con las opciones elegidas',str(e))
        iniciar_server()

# Atiende las diferentes peticiones
def correr_server():
    serverNum = 0
    server.listen(25)
    print(f"Server escuchando en {SERVER}")
    # Acepta todas las conexiones e inicia un thread para enviar cuando todos esten listos
    while True:
        try:
            conn, addr = server.accept()
            server.setblocking(1)
            client = ClientThread(conn,addr,serverNum)
            serverNum = serverNum + 1
            global all_conns
            all_conns.append(client)
            client.start()
            print ('Nueva conexion de ', addr)
            if len(all_conns) == num_usuarios:
                print('Los usuarios estan todos conectados!')
                
                flag_enviado = False
                while not flag_enviado:
                    all_ready = True
                    for conns in all_conns:
                        all_ready = conns.ready and all_ready                        
                    flag_enviado = all_ready
                for conns in all_conns:
                    conns.send = flag_enviado
                del all_conns[:]

        except Exception as e:
            print ('Fallo al conseguir las conexiones', str(e))
    server.close()

# Thread que da manejo a cada cliente
class ClientThread(threading.Thread):
    def __init__(self, conn, addr,serverNum):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.ready = False
        self.terminar = True
        self.send = False
        self.serverNum =  serverNum
    
    def run(self):
        # Saluda al cliente
        self.conn.send("Connected with server".encode(FORMAT))
        # Recibe que el cliente esta listo
        msg = self.conn.recv(255).decode(FORMAT)
        
        if msg == "Ready":
            #Se crea el log para escribir los resultados
            name = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())+'-log'+str(self.serverNum)+'.txt'
            log = open(path.join(logs_path, name),'w')
            
            self.ready = True
            console_msg = 'La conexion {} esta lista \n'.format(self.addr)
            print (console_msg)
            log.write('Se le envia al cliente {} \n'.format(self.addr))

            
            #Espera a poder enviar
            while self.terminar and not self.send:
                continue
            if self.terminar and self.send:
                self.conn.send(file_name.encode(FORMAT))
                log.write('Se envia el archivo {} \n'.format(file_name))
                log.write('El archivo pesa {} \n'.format(file_size))
                
                # Se abre el archivo
                f = open(file_path, 'rb')
                
                #Se encapsula el tamano y se envia 
                file_size_encoded = st.pack('I', file_size)
                self.conn.send(file_size_encoded)
                line = f.read(1024)
                start_time = time.time()
                
                # Se itera sobre el archivo para enviarse por paquetes
                while line:
                    self.conn.send(line)
                    line = f.read(1024)
                    
                estado_transferencia = self.conn.recv(255).decode(FORMAT)
                console_msg = 'La conexion {} dice {} \n'.format(self.addr,estado_transferencia)
                print (console_msg)
                
                # Se le envia nuestro hash para que el cliente verifique
                self.conn.send(hash_local)
                
                # Se lee si el cliente confirma que fue correcto o no
                envio_correcto = self.conn.recv(255).decode(FORMAT)
                if envio_correcto == "ok":
                    log.write('El archivo se envio satisfactoriamente \n')
                else:
                    log.write('El archivo no se envio satisfactoriamente\n')
                
                # Se toma y envia el tiempo al cliente
                stop_time = float(st.unpack('d',self.conn.recv(8))[0])
                total_time = abs(start_time - stop_time)
                self.conn.send(st.pack('d',total_time))
                
                # Se registra el tiempo y se cierra
                log.write('Tiempo de transmicion fue: {} s \n'.format(round(total_time,3) ))
                log.close()
                self.conn.close()
            else:
                log.close()
                self.conn.close()
                    
                
iniciar_server()
correr_server()