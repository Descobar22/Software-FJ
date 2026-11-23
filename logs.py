# Importamos logging para guardar los eventos y errores
import logging

# Configuramos el registro del sistema
logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Creamos una función para guardar las acciones del sistema
def registrar_evento(mensaje):
    logging.info(mensaje)


# Creamos una función para guardar los errores
def registrar_error(mensaje):
    logging.error(mensaje)