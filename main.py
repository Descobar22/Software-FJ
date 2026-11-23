# Importamos las herramientas necesarias
from abc import ABC, abstractmethod
import re
from logs import registrar_evento, registrar_error
from functools import singledispatchmethod


# EXCEPCIONES PERSONALIZADAS

# Excepción general del sistema
class ErrorSistema(Exception):
    pass

# Errores relacionados con los datos
class DatosInvalidosError(ErrorSistema):
    pass

# Errores de clientes y servicios
class ClienteNoEncontradoError(ErrorSistema):
    pass

class ServicioNoDisponibleError(ErrorSistema):
    pass

class ReservaInvalidaError(ErrorSistema):
    pass

class OperacionNoPermitidaError(ErrorSistema):
    pass

class CalculoInconsistenteError(ErrorSistema):
    pass


# CLASE ABSTRACTA GENERAL

# Sirve como base para las demás clases
class EntidadSistema(ABC):

    def __init__(self, identificador):
        self.__identificador = identificador

    # Permitimos consultar el identificador
    @property
    def identificador(self):
        return self.__identificador

    # Métodos que deben implementar las clases hijas
    @abstractmethod
    def validar(self):
        pass

    @abstractmethod
    def mostrar_informacion(self):
        pass


# CLASE CLIENTE

class Cliente(EntidadSistema):

    def __init__(self, identificador, nombre, documento, correo, telefono):
        super().__init__(identificador)

        # Guardamos los datos del cliente
        self.__nombre = nombre
        self.__documento = documento
        self.__correo = correo
        self.__telefono = telefono

        self.validar()
        registrar_evento(f"Cliente {identificador} registrado.")

    # Consultamos los datos del cliente
    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    # Revisamos que los datos sean correctos
    def validar(self):
        if not isinstance(self.identificador, str) or not self.identificador.strip():
            raise DatosInvalidosError("El identificador es obligatorio.")

        if not isinstance(self.__nombre, str) or not self.__nombre.strip():
            raise DatosInvalidosError("El nombre es obligatorio.")

        if not isinstance(self.__documento, str) or not re.fullmatch(r"\d{6,12}", self.__documento):
            raise DatosInvalidosError("El documento debe tener entre 6 y 12 dígitos.")

        patron = r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$"
        if not isinstance(self.__correo, str) or not re.fullmatch(patron, self.__correo):
            raise DatosInvalidosError("El correo electrónico no es válido.")

        if not isinstance(self.__telefono, str) or not re.fullmatch(r"\d{10}", self.__telefono):
            raise DatosInvalidosError("El teléfono debe tener 10 dígitos.")

    # Mostramos la información del cliente
    def mostrar_informacion(self):
        return (
            f"Identificador: {self.identificador}\n"
            f"Nombre: {self.nombre}\n"
            f"Documento: {self.documento}\n"
            f"Correo: {self.correo}\n"
            f"Teléfono: {self.telefono}"
        )


# CLASE ABSTRACTA SERVICIO

class Servicio(EntidadSistema):

    def __init__(self, identificador, nombre, precio_base):
        super().__init__(identificador)

        # Guardamos los datos del servicio
        self.__nombre = nombre
        self.__precio_base = precio_base
        self.validar()

    @property
    def nombre(self):
        return self.__nombre

    @property
    def precio_base(self):
        return self.__precio_base

    # Validamos los datos del servicio
    def validar(self):
        if not isinstance(self.identificador, str) or not self.identificador.strip():
            raise DatosInvalidosError("El identificador es obligatorio.")

        if not isinstance(self.__nombre, str) or not self.__nombre.strip():
            raise DatosInvalidosError("El nombre del servicio es obligatorio.")

        if (not isinstance(self.__precio_base, (int, float))
                or isinstance(self.__precio_base, bool)
                or self.__precio_base <= 0):
            raise DatosInvalidosError("El precio debe ser mayor que cero.")

    # Cada servicio calcula su propio costo
    @abstractmethod
    def calcular_costo(self, cantidad):
        pass

    # Calculamos el costo final con impuestos y descuentos opcionales
    def calcular_costo_final(self, cantidad, impuesto=0, descuento=0):
        if (not isinstance(impuesto, (int, float))
                or isinstance(impuesto, bool)
                or not 0 <= impuesto <= 100):
            raise DatosInvalidosError("El impuesto debe estar entre 0 y 100.")

        if (not isinstance(descuento, (int, float))
                or isinstance(descuento, bool)
                or not 0 <= descuento <= 100):
            raise DatosInvalidosError("El descuento debe estar entre 0 y 100.")

        costo = self.calcular_costo(cantidad)
        costo_con_descuento = costo - (costo * descuento / 100)
        total = costo_con_descuento + (costo_con_descuento * impuesto / 100)

        return total

    # Aplicamos ajustes según el tipo de dato recibido
    @singledispatchmethod
    def aplicar_ajuste(self, ajuste):
        raise DatosInvalidosError("Tipo de ajuste no válido.")

    @aplicar_ajuste.register
    def _(self, ajuste: int):
        if isinstance(ajuste, bool):
            raise DatosInvalidosError("El ajuste no puede ser booleano.")
        return self.precio_base + ajuste

    @aplicar_ajuste.register
    def _(self, ajuste: float):
        return self.precio_base * (1 + ajuste)

# SERVICIOS ESPECÍFICOS

# Calculamos el costo según las horas de uso
class ReservaSala(Servicio):

    def calcular_costo(self, horas):
        if not isinstance(horas, (int, float)) or isinstance(horas, bool) or horas <= 0:
            raise DatosInvalidosError("Las horas deben ser mayores que cero.")
        return self.precio_base * horas

    def mostrar_informacion(self):
        return f"Sala: {self.nombre} - Precio por hora: ${self.precio_base}"


# Controlamos el alquiler y la disponibilidad de equipos
class AlquilerEquipo(Servicio):

    def __init__(self, identificador, nombre, precio_base, stock=10):
        super().__init__(identificador, nombre, precio_base)

        if not isinstance(stock, int) or isinstance(stock, bool) or stock < 0:
            raise DatosInvalidosError("El stock debe ser un entero positivo.")

        self.__stock = stock

    def calcular_costo(self, cantidad):
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise DatosInvalidosError("La cantidad debe ser un número entero positivo.")

        if cantidad > self.__stock:
            raise ServicioNoDisponibleError("No hay suficientes equipos disponibles.")

        return self.precio_base * cantidad

    def mostrar_informacion(self):
        return (
            f"Equipo: {self.nombre} - Precio por unidad: ${self.precio_base} "
            f"- Disponibles: {self.__stock}"
        )

    @property
    def stock(self):
        return self.__stock

    def disminuir_stock(self, cantidad):
        if cantidad > self.__stock:
            raise ServicioNoDisponibleError(
                "No hay suficientes equipos disponibles."
            )
        self.__stock -= cantidad

# Calculamos el costo de la asesoría según las horas contratadas
class AsesoriaEspecializada(Servicio):

    def calcular_costo(self, horas):
        if (not isinstance(horas, (int, float))
                or isinstance(horas, bool)
                or horas <= 0):
            raise DatosInvalidosError(
                "Las horas de asesoría deben ser mayores que cero."
            )

        return self.precio_base * horas

    def mostrar_informacion(self):
        return (
            f"Asesoría: {self.nombre} "
            f"- Precio por hora: ${self.precio_base}"
        )


# CLASE RESERVA

# Relacionamos un cliente con un servicio
class Reserva(EntidadSistema):

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = duracion
        self.__estado = "Pendiente"
        self.validar()

    @property
    def estado(self):
        return self.__estado

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    # Revisamos los datos de la reserva
    def validar(self):
        if not isinstance(self.__cliente, Cliente):
            raise ReservaInvalidaError("El cliente no es válido.")

        if not isinstance(self.__servicio, Servicio):
            raise ReservaInvalidaError("El servicio no es válido.")

        if (not isinstance(self.__duracion, (int, float))
                or isinstance(self.__duracion, bool)
                or self.__duracion <= 0):
            raise ReservaInvalidaError("La duración debe ser mayor que cero.")

    # Confirmamos la reserva
    def confirmar(self):
        if self.__estado != "Pendiente":
            raise OperacionNoPermitidaError("La reserva no se puede confirmar.")

        self.__estado = "Confirmada"
        registrar_evento(f"Reserva {self.identificador} confirmada.")

    # Cancelamos la reserva
    def cancelar(self):
        if self.__estado not in ("Pendiente", "Confirmada"):
            raise OperacionNoPermitidaError("La reserva no se puede cancelar.")

        self.__estado = "Cancelada"
        registrar_evento(f"Reserva {self.identificador} cancelada.")

    # Calculamos el costo de la reserva
    def procesar(self):
        if self.__estado != "Confirmada":
            raise OperacionNoPermitidaError("Primero confirma la reserva.")

        try:
            costo = self.__servicio.calcular_costo(self.__duracion)
        except DatosInvalidosError as error:
            raise CalculoInconsistenteError(
                "No fue posible calcular el costo de la reserva."
            ) from error

        if isinstance(self.__servicio, AlquilerEquipo):
            self.__servicio.disminuir_stock(self.__duracion)

        self.__estado = "Procesada"
        registrar_evento(f"Reserva {self.identificador} procesada.")
        return costo
    
    # Mostramos los datos de la reserva
    def mostrar_informacion(self):
        return (
            f"Reserva: {self.identificador}\n"
            f"Cliente: {self.__cliente.nombre}\n"
            f"Servicio: {self.__servicio.nombre}\n"
            f"Estado: {self.__estado}"
        )


# CLASE PARA ADMINISTRAR EL SISTEMA

# Guardamos los clientes, servicios y reservas
class SistemaGestion:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    # Registramos un cliente
    def registrar_cliente(self, cliente):
        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise DatosInvalidosError("El cliente ya está registrado.")

        self.clientes.append(cliente)
        registrar_evento("Cliente agregado al sistema.")

    # Registramos un servicio
    def registrar_servicio(self, servicio):
        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise DatosInvalidosError("El servicio ya está registrado.")

        self.servicios.append(servicio)
        registrar_evento("Servicio agregado al sistema.")

    # Buscamos un cliente por su identificador
    def buscar_cliente(self, identificador):
        for cliente in self.clientes:
            if cliente.identificador == identificador:
                return cliente

        raise ClienteNoEncontradoError("El cliente no está registrado.")

    # Buscamos un servicio por su identificador
    def buscar_servicio(self, identificador):
        for servicio in self.servicios:
            if servicio.identificador == identificador:
                return servicio

        raise ServicioNoDisponibleError("El servicio no está registrado.")

    # Creamos una reserva
    def registrar_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise ReservaInvalidaError("La reserva no es válida.")

        self.buscar_cliente(reserva._Reserva__cliente.identificador)
        self.buscar_servicio(reserva._Reserva__servicio.identificador)

        if any(r.identificador == reserva.identificador for r in self.reservas):
            raise ReservaInvalidaError("La reserva ya existe.")

        self.reservas.append(reserva)
        registrar_evento("Reserva agregada al sistema.")

    # Mostramos las reservas registradas
    def listar_reservas(self):
        if not self.reservas:
            print("No hay reservas registradas.")
            return

        for reserva in self.reservas:
            print(reserva.mostrar_informacion())
            print("-------------------------")




# PRUEBAS INICIALES

if __name__ == "__main__":

    # Creamos el sistema de gestión
    sistema = SistemaGestion()

    print("================================")
    print("       SISTEMA SOFTWARE FJ")
    print("================================")

    # OPERACIÓN 1: Registrar un cliente válido
    # Probamos el registro de un cliente
    try:
        cliente1 = Cliente(
            "C001", "Laura Salamanca", "103053315",
            "laura@gmail.com", "3001234567"
        )

        # Guardamos el cliente en el sistema
        sistema.registrar_cliente(cliente1)

        print("\nCliente registrado correctamente.")
        print(cliente1.mostrar_informacion())

    except DatosInvalidosError as error:
        print(f"\nNo se pudo registrar el cliente: {error}")
        registrar_error(f"Error al registrar cliente: {error}")

    # OPERACIÓN 2: Intentar registrar un cliente con correo incorrecto
    # Probamos un correo incorrecto
    try:
        cliente2 = Cliente(
            "C002", "Carlos Perez", "105123423",
            "correo_incorrecto", "3101458901"
        )
        print(cliente2.mostrar_informacion())

    except DatosInvalidosError as error:
        print(f"\nError controlado: {error}")
        registrar_error(f"Error al registrar cliente: {error}")

    # OPERACIÓN 3: Crear y registrar los servicios disponibles
    # Creamos los servicios disponibles
    try:
        sala = ReservaSala("S001", "Sala de reuniones", 50000)
        equipo = AlquilerEquipo("S002", "Computador portátil", 30000)
        asesoria = AsesoriaEspecializada("S003", "Asesoría en sistemas", 60000)

        # Guardamos los servicios en el sistema
        sistema.registrar_servicio(sala)
        sistema.registrar_servicio(equipo)
        sistema.registrar_servicio(asesoria)

        # Mostramos los servicios
        print("\n========== SERVICIOS ==========")
        print(sala.mostrar_informacion())
        print(equipo.mostrar_informacion())
        print(asesoria.mostrar_informacion())

        # OPERACIÓN 4: Calcular los costos de los servicios
        # Comprobamos los cálculos
        print("\n========== COSTOS ==========")
        print(f"Sala por 2 horas: ${sala.calcular_costo(2)}")
        print(f"3 equipos: ${equipo.calcular_costo(3)}")
        print(f"Asesoría por 2 horas: ${asesoria.calcular_costo(2)}")

        # OPERACIÓN 5: Solicitar más equipos de los disponibles
        # Probamos una cantidad superior al inventario
        try:
            equipo.calcular_costo(15)
        except ServicioNoDisponibleError as error:
            print(f"\nDisponibilidad: {error}")
            registrar_error(f"Error de inventario: {error}")

        # OPERACIÓN 6: Calcular un servicio aplicando descuento e impuesto
        # Probamos el cálculo con descuento e impuesto
        total = sala.calcular_costo_final(2, impuesto=19, descuento=10)
        print(f"\nSala con 10% de descuento y 19% de impuesto: ${total:.0f}")

        # OPERACIÓN 7: Crear y registrar una reserva
        # Creamos una reserva pendiente
        reserva1 = Reserva("R001", cliente1, sala, 2)
        sistema.registrar_reserva(reserva1)

        # OPERACIÓN 8: Intentar procesar una reserva sin confirmarla
        # Intentamos procesarla sin confirmarla
        try:
            reserva1.procesar()
        except OperacionNoPermitidaError as error:
            print(f"\nOperación no permitida: {error}")
            registrar_error(f"Error al procesar reserva: {error}")

        # OPERACIÓN 9: Probar el cálculo con una cantidad inválida
        # Probamos un cálculo con una cantidad inválida
        try:
            prueba = AlquilerEquipo("S004", "Equipo de prueba", 30000)
            prueba.calcular_costo(-2)
        except DatosInvalidosError as error:
            try:
                raise CalculoInconsistenteError(
                    "No se pudo realizar el cálculo."
                ) from error
            except CalculoInconsistenteError as error_encadenado:
                print(f"\nError de cálculo: {error_encadenado}")
                print(f"Causa original: {error_encadenado.__cause__}")
                registrar_error(f"Error de cálculo: {error_encadenado}")

        # OPERACIÓN 10: Confirmar la reserva
        # Confirmamos la reserva
        reserva1.confirmar()

        # OPERACIÓN 11: Intentar registrar una reserva duplicada
        # Intentamos registrar una reserva con el mismo código
        try:
            reserva_duplicada = Reserva("R001", cliente1, sala, 1)
            sistema.registrar_reserva(reserva_duplicada)
        except ReservaInvalidaError as error:
            print(f"\nError controlado: {error}")
            registrar_error(f"Error al registrar reserva: {error}")

        print("\n========== RESERVA ==========")
        print(reserva1.mostrar_informacion())

        # OPERACIÓN 12: Procesar la reserva confirmada
        # Procesamos la reserva y controlamos posibles errores
        try:
            costo = reserva1.procesar()
        except OperacionNoPermitidaError as error:
            print(f"No se pudo procesar: {error}")
            registrar_error(f"Error de procesamiento: {error}")
        else:
            print(f"Costo de la reserva: ${costo}")
        finally:
            print("Proceso de reserva finalizado.")

        # Mostramos los registros del sistema
        print("\n========== REGISTROS ==========")
        print(f"Clientes: {len(sistema.clientes)}")
        print(f"Servicios: {len(sistema.servicios)}")
        print(f"Reservas: {len(sistema.reservas)}")

        # Mostramos las reservas registradas
        print("\n========== LISTADO DE RESERVAS ==========")
        sistema.listar_reservas()

        # OPERACIÓN 13: Registrar y cancelar una reserva
        # Probamos la cancelación de una reserva
        try:
            reserva2 = Reserva("R002", cliente1, asesoria, 1)
            sistema.registrar_reserva(reserva2)
            reserva2.cancelar()

            print("\n========== CANCELACIÓN ==========")
            print(reserva2.mostrar_informacion())

        except (ReservaInvalidaError, OperacionNoPermitidaError) as error:
            print(f"Error al cancelar la reserva: {error}")
            registrar_error(f"Error de cancelación: {error}")

        # OPERACIÓN 14: Intentar cancelar nuevamente una reserva ya cancelada
        # Intentamos cancelar nuevamente la reserva
        try:
            reserva2.cancelar()
        except OperacionNoPermitidaError as error:
            print(f"\nCancelación no permitida: {error}")
            registrar_error(f"Error de cancelación: {error}")

        # Probamos las búsquedas
        print("\n========== BÚSQUEDAS ==========")
        print(sistema.buscar_cliente("C001").nombre)
        print(sistema.buscar_servicio("S001").nombre)

        # OPERACIÓN 15: Buscar un cliente que no está registrado
        # Probamos la búsqueda de un cliente inexistente
        try:
            sistema.buscar_cliente("C999")
        except ClienteNoEncontradoError as error:
            print(f"Error controlado: {error}")
            registrar_error(f"Error de búsqueda: {error}")

    except DatosInvalidosError as error:
        print(f"\nError en los servicios: {error}")
        registrar_error(f"Error en los servicios: {error}")