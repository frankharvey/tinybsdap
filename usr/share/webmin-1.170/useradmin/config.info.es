line0=Archivos de usuario y grupo,11
passwd_file=Archivo de clave de acceso,3,Generado
group_file=Archivo de grupo,0
shadow_file=Archivo de clave de acceso en la sombra (Shadow),3
master_file=Archivo de clave de acceso maestra BSD,3
gshadow_file=Archivo de grupo en la sombra (Shadow),3
pre_command=Comando a ejecutar antes de realizar cambios,0
post_command=Comando a ejecutar tras realizar cambios,0

line1=Opciones de directorio inicial,11
homedir_perms=Permisos de los nuevos directorios iniciales,0
user_files=Copiar archivos a nuevos directorios iniciales desde,9,40,3
home_base=Base de directorio inicial autom�tica,3,Sin poner
home_style=Estilo de directorio inicial autom�tico,4,0-home/nombre_de_usuario,1-home/u/nombre_de_usuario,2-home/u/us/nombre_de_usuario,3-home/u/s/nombre_de_usuario

line2=Opciones de nuevo usuario,11
base_uid=UID m�s baja para nuevos usuarios,0,5
base_gid=GID m�s baja para nuevos grupos,0,5
new_user_group=Crear nuevo grupo para nuevos usurios,1,1-S�,0-No
skip_md5=no usar claves de acceso MD5 si falta el m�dulo MD5 de perl,1,1-S�,0-No
alias_check=Revisar por choques de alias de sendmail,1,1-S�,0-No
delete_only=�S�lo borrar archivos pertenecientes al usuario?,1,1-S�,0-No
max_length=Medida m�xima de nombre de usuario y grupo,3,Ilimitada

line3=Valores por de defecto de nuevo usuario,11
default_group=Grupo por defecto para nuevos usuarios,6,Por defecto
default_shell=Shell por defecto para nuevos usuarios,3,Primero de la lista
default_min=D�as m�nimo por defecto para nuevos usurios,3,Ninguno
default_max=D�as m�ximo por defecto para nuevos usuarios,3,Ninguno
default_warn=D�as de aviso por defecto para nuevos usuarios,3,Ninguno
default_inactive=Default inactive days for new users,3,None

line4=Opciones a mostrar,11
display_max=N�mero de usuarios m�ximo a mostrar,0
sort_mode=Clasificar usuarios y grupo por,4,0-Orden en archivo,1-Nombre de usuario,2-Nombre real,3-Alias,4-Shell,5-UID o GID,6-Directorio inicial
last_count=N�mero de logins previos a mostrarm,3,Ilimitado
display_mode=Mostrar usuarios y grupos por,1,2-Grupo primario categorizado,1-Detalles completos,0-S�lo nombre
passwd_stars=�Ocultar clave de acceso de s�lo texto?,1,1-S�,0-No
from_files=Obtener informaci�n de usuario y grupo desde,1,1-Archivos,0-Llamadas a sistema
random_password=�Genero clave de acceso para nuevos usuarios?,1,1-S�,0-No
extra_real=�Muestro detalles de oficina y tel�fono?,1,1-S�,0-No
