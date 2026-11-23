# Importamos la herramienta para guardar los registros 
import logging

# Configuramos el archivo donde se guardarán los eventos 
logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Guardamos las acciones realizadas en el sistema 
def registrar_evento(mensaje):
    logging.info(mensaje)

# Guardamos los errores que se presenten
def registrar_error(mensaje):
    logging.error(mensaje)