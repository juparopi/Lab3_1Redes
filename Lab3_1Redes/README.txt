# lab3_redes

Para correr correctamente el script antes de todo hay que configurar las ip y los puertos de forma en la que haya comunicacion entre el server y el cliente.
Crear en el servidor una carpeta llamada 'logs'
Tambien hay que crear los dos archivos de prueba en una carpeta llamada 'archivos' dentro de la carpeta de server. Estos dos archivos deben llamarse '100.txt' y '250.txt'.

Para crear estos archivos dentro de terminal de Windowns correr los comandos: 
fsutil file createnew 100.txt 104857600  
fsutil file createnew 250.txt length 262144000 

Para crear estos archivos dentro de la terminal de Linux correr los comandos: 
dd if=/dev/zero of=100.txt count=1048576 bs=100 
dd if=/dev/zero of=250.txt count=1048576 bs=250

Crear en el cliente una carpeta llamada 'logs' y otra carpeta llamada 'archivos'
