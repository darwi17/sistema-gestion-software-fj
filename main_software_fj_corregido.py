import logging
import math
import re
from abc import ABC, abstractmethod
from datetime import datetime

# ============================================================
# CONFIGURACIÓN DE REGISTROS
# ============================================================
LOG_FILE = "sistema_software_fj_corregido.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
    force=True,
)


# ============================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================
class ExcepcionSistemaFJ(Exception):
    """Excepción base del sistema Software FJ."""


class DatoInvalidoError(ExcepcionSistemaFJ):
    """Se genera cuando un dato no cumple las validaciones."""


class ServicioNoDisponibleError(ExcepcionSistemaFJ):
    """Se genera cuando un servicio o sus parámetros no son válidos."""


class ReservaIncorrectaError(ExcepcionSistemaFJ):
    """Se genera cuando una reserva no puede procesarse."""


# ============================================================
# FUNCIONES AUXILIARES DE VALIDACIÓN
# ============================================================
def validar_numero(valor, nombre, minimo=None, maximo=None):
    """Valida números reales, finitos y dentro del rango indicado."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise DatoInvalidoError(f"{nombre} debe ser un número.")
    if not math.isfinite(valor):
        raise DatoInvalidoError(f"{nombre} debe ser un número finito.")
    if minimo is not None and valor < minimo:
        raise DatoInvalidoError(f"{nombre} no puede ser menor que {minimo}.")
    if maximo is not None and valor > maximo:
        raise DatoInvalidoError(f"{nombre} no puede ser mayor que {maximo}.")
    return float(valor)


def validar_entero(valor, nombre, minimo=1):
    """Valida que un dato sea un entero y no un booleano."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise DatoInvalidoError(f"{nombre} debe ser un número entero.")
    if valor < minimo:
        raise DatoInvalidoError(f"{nombre} debe ser como mínimo {minimo}.")
    return valor


# ============================================================
# CLASE ABSTRACTA GENERAL
# ============================================================
class EntidadGeneral(ABC):
    """Representa una entidad general del sistema."""

    def __init__(self, identificador: str):
        if not isinstance(identificador, str) or not identificador.strip():
            raise DatoInvalidoError("El identificador no puede estar vacío.")
        self._identificador = identificador.strip()

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def obtener_detalles(self) -> str:
        """Devuelve los detalles de la entidad."""


# ============================================================
# CLASE CLIENTE
# ============================================================
class Cliente(EntidadGeneral):
    """Cliente con datos encapsulados y validados."""

    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str):
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str):
            raise DatoInvalidoError("El correo debe ser texto.")
        valor = valor.strip()
        patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(patron, valor):
            raise DatoInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not isinstance(valor, str) or not valor.isdigit() or not 7 <= len(valor) <= 15:
            raise DatoInvalidoError(
                "El teléfono debe contener entre 7 y 15 dígitos, sin letras."
            )
        self._telefono = valor

    def obtener_detalles(self) -> str:
        return (
            f"Cliente [ID: {self.identificador}, Nombre: {self.nombre}, "
            f"Correo: {self.correo}, Teléfono: {self.telefono}]"
        )


# ============================================================
# CLASE ABSTRACTA SERVICIO
# ============================================================
class Servicio(EntidadGeneral, ABC):
    """Define la estructura común de los servicios."""

    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float):
        super().__init__(identificador)
        if not isinstance(nombre_servicio, str) or not nombre_servicio.strip():
            raise DatoInvalidoError("El nombre del servicio no puede estar vacío.")
        self.nombre_servicio = nombre_servicio.strip()
        self.costo_base = costo_base

    @property
    def costo_base(self):
        return self._costo_base

    @costo_base.setter
    def costo_base(self, valor):
        self._costo_base = validar_numero(valor, "El costo base", minimo=0)

    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        """Calcula el costo de acuerdo con el tipo de servicio."""

    @abstractmethod
    def describir_servicio(self) -> str:
        """Describe las características del servicio."""

    def obtener_detalles(self) -> str:
        # Implementa el método abstracto heredado por EntidadGeneral.
        return self.describir_servicio()


# ============================================================
# SERVICIO 1: RESERVA DE SALA
# ============================================================
class ReservaSala(Servicio):
    def __init__(self, identificador, costo_base, capacidad, proyector):
        super().__init__(identificador, "Reserva de Sala", costo_base)
        self.capacidad = validar_entero(capacidad, "La capacidad")
        if not isinstance(proyector, bool):
            raise DatoInvalidoError("El dato proyector debe ser verdadero o falso.")
        self.proyector = proyector

    def calcular_costo(self, horas: int = 1, descuento_porcentaje: float = 0.0) -> float:
        validar_entero(horas, "Las horas")
        descuento = validar_numero(
            descuento_porcentaje, "El descuento", minimo=0, maximo=100
        )
        total = self.costo_base * horas
        if self.proyector:
            total += 20.0
        total *= 1 - (descuento / 100)
        return round(total, 2)

    def describir_servicio(self) -> str:
        return (
            f"Sala ID: {self.identificador}, capacidad: {self.capacidad} personas, "
            f"proyector: {'Sí' if self.proyector else 'No'}"
        )


# ============================================================
# SERVICIO 2: ALQUILER DE EQUIPOS
# ============================================================
class AlquilerEquipo(Servicio):
    def __init__(self, identificador, costo_base, tipo_equipo, seguro_incluido):
        super().__init__(identificador, "Alquiler de Equipo", costo_base)
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise DatoInvalidoError("El tipo de equipo no puede estar vacío.")
        if not isinstance(seguro_incluido, bool):
            raise DatoInvalidoError("Seguro incluido debe ser verdadero o falso.")
        self.tipo_equipo = tipo_equipo.strip()
        self.seguro_incluido = seguro_incluido

    def calcular_costo(self, dias: int = 1, incluir_impuesto: bool = True) -> float:
        validar_entero(dias, "Los días de alquiler")
        if not isinstance(incluir_impuesto, bool):
            raise DatoInvalidoError("incluir_impuesto debe ser verdadero o falso.")
        subtotal = self.costo_base * dias
        if not self.seguro_incluido:
            subtotal += 15.0
        if incluir_impuesto:
            subtotal *= 1.19
        return round(subtotal, 2)

    def describir_servicio(self) -> str:
        return (
            f"Equipo: {self.tipo_equipo} (ID: {self.identificador}), "
            f"seguro incluido: {'Sí' if self.seguro_incluido else 'No'}"
        )


# ============================================================
# SERVICIO 3: ASESORÍA ESPECIALIZADA
# ============================================================
class AsesoriaEspecializada(Servicio):
    def __init__(self, identificador, costo_base, area_experta, nivel_senior):
        super().__init__(identificador, "Asesoría Especializada", costo_base)
        if not isinstance(area_experta, str) or not area_experta.strip():
            raise DatoInvalidoError("El área de asesoría no puede estar vacía.")
        if not isinstance(nivel_senior, bool):
            raise DatoInvalidoError("nivel_senior debe ser verdadero o falso.")
        self.area_experta = area_experta.strip()
        self.nivel_senior = nivel_senior

    def calcular_costo(self, sesiones: int = 1, bono_calidad: float = 0.0) -> float:
        validar_entero(sesiones, "Las sesiones")
        bono = validar_numero(bono_calidad, "El bono de calidad", minimo=0)
        multiplicador = 1.5 if self.nivel_senior else 1.0
        return round((self.costo_base * sesiones * multiplicador) + bono, 2)

    def describir_servicio(self) -> str:
        nivel = "Senior" if self.nivel_senior else "Junior"
        return (
            f"Asesoría en {self.area_experta} (ID: {self.identificador}), "
            f"nivel: {nivel}"
        )


# ============================================================
# CLASE RESERVA
# ============================================================
class Reserva:
    """Relaciona cliente, servicio, duración, costo y estado."""

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio):
        if not isinstance(id_reserva, str) or not id_reserva.strip():
            raise DatoInvalidoError("El ID de reserva no puede estar vacío.")
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva debe recibir un objeto Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva debe recibir un objeto Servicio.")
        self.id_reserva = id_reserva.strip()
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = None
        self.estado = "Creada"
        self.costo_final = 0.0

    def procesar_reserva(self, *args, **kwargs):
        """Calcula el costo y confirma la reserva si todo resulta correcto."""
        logging.info("Iniciando procesamiento de la reserva %s.", self.id_reserva)
        if self.estado != "Creada":
            raise ReservaIncorrectaError(
                f"No se puede procesar una reserva en estado '{self.estado}'."
            )

        try:
            if not self.cliente or not self.servicio:
                raise ReservaIncorrectaError(
                    "La reserva no tiene cliente o servicio asignado."
                )

            # Identifica y conserva la duración recibida según el servicio.
            claves_duracion = ("horas", "dias", "sesiones")
            duracion = next(
                (kwargs[clave] for clave in claves_duracion if clave in kwargs),
                args[0] if args else 1,
            )
            self.costo_final = self.servicio.calcular_costo(*args, **kwargs)
            self.duracion = duracion

        except (DatoInvalidoError, ServicioNoDisponibleError) as error:
            logging.exception("Error de validación en reserva %s.", self.id_reserva)
            raise ReservaIncorrectaError(
                f"No fue posible procesar la reserva {self.id_reserva}."
            ) from error
        except Exception as error:
            logging.exception("Error inesperado en reserva %s.", self.id_reserva)
            raise ReservaIncorrectaError(
                f"Error inesperado al procesar la reserva {self.id_reserva}."
            ) from error
        else:
            self.estado = "Confirmada"
            logging.info(
                "Reserva %s confirmada. Duración: %s. Costo: $%.2f.",
                self.id_reserva, self.duracion, self.costo_final
            )
            return self.costo_final
        finally:
            print(
                f"[FINALIZADO] Reserva {self.id_reserva}: "
                f"estado actual = {self.estado}."
            )

    def cancelar_reserva(self):
        """Cancela una reserva que no haya sido cancelada previamente."""
        try:
            if self.estado == "Cancelada":
                raise ReservaIncorrectaError(
                    f"La reserva {self.id_reserva} ya estaba cancelada."
                )
            if self.estado != "Confirmada":
                raise ReservaIncorrectaError(
                    f"No se puede cancelar una reserva en estado '{self.estado}'."
                )
            self.estado = "Cancelada"
            logging.info("Reserva %s cancelada correctamente.", self.id_reserva)
            print(f"Reserva {self.id_reserva} cancelada correctamente.")
        except ReservaIncorrectaError:
            logging.exception("No se pudo cancelar la reserva %s.", self.id_reserva)
            raise

    def obtener_detalles(self):
        return (
            f"Reserva {self.id_reserva} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre_servicio} | Duración: {self.duracion} | "
            f"Estado: {self.estado} | Total: ${self.costo_final:.2f}"
        )


# ============================================================
# SIMULACIÓN DE DIEZ OPERACIONES
# ============================================================
def ejecutar_simulacion():
    print("=" * 65)
    print(" SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ | FASE 4")
    print("=" * 65)
    logging.info("========== INICIO DE LA SIMULACIÓN ==========")

    lista_reservas = []
    resultados = []

    def ejecutar_operacion(numero, descripcion, accion):
        print(f"\n--- Operación {numero}: {descripcion} ---")
        try:
            resultado = accion()
        except Exception as error:
            resultados.append((numero, "Error controlado"))
            print(f"Error controlado: {error}")
            logging.warning(
                "Operación %s fallida de forma controlada: %s", numero, error
            )
        else:
            resultados.append((numero, "Correcta"))
            if resultado is not None:
                print(resultado)
            logging.info("Operación %s completada correctamente.", numero)

    # 1. Reserva de sala exitosa.
    def op1():
        cliente = Cliente("C001", "Ana María Pérez", "ana.perez@softwarefj.com", "3104567890")
        servicio = ReservaSala("S001", 50.0, 20, True)
        reserva = Reserva("R001", cliente, servicio)
        costo = reserva.procesar_reserva(horas=3, descuento_porcentaje=10)
        lista_reservas.append(reserva)
        return f"{reserva.obtener_detalles()}"

    ejecutar_operacion(1, "Reserva de sala exitosa", op1)

    # 2. Correo inválido.
    def op2():
        Cliente("C002", "Carlos Gómez", "correo-sin-arroba.com", "3201234567")
    ejecutar_operacion(2, "Registro de cliente con correo inválido", op2)

    # 3. Alquiler de equipo exitoso.
    def op3():
        cliente = Cliente("C003", "Lucía Benítez", "lucia.benitez@gmail.com", "3159876543")
        servicio = AlquilerEquipo("EQ01", 120.0, "Servidor Rack", False)
        reserva = Reserva("R003", cliente, servicio)
        reserva.procesar_reserva(dias=5, incluir_impuesto=True)
        lista_reservas.append(reserva)
        return reserva.obtener_detalles()
    ejecutar_operacion(3, "Alquiler de equipo exitoso", op3)

    # 4. Duración negativa.
    def op4():
        cliente = Cliente("C004", "Pedro Gómez", "pedro.gomez@gmail.com", "3104567891")
        servicio = AlquilerEquipo("EQ02", 80.0, "Laptop Dell", True)
        reserva = Reserva("R004", cliente, servicio)
        reserva.procesar_reserva(dias=-2)
    ejecutar_operacion(4, "Alquiler con días negativos", op4)

    # 5. Asesoría senior exitosa.
    def op5():
        cliente = Cliente("C005", "Mateo Rincón", "mateo.rincon@unad.edu.co", "3007894561")
        servicio = AsesoriaEspecializada("AS01", 200.0, "Arquitectura de Software", True)
        reserva = Reserva("R005", cliente, servicio)
        reserva.procesar_reserva(sesiones=2, bono_calidad=50.0)
        lista_reservas.append(reserva)
        return reserva.obtener_detalles()
    ejecutar_operacion(5, "Asesoría especializada senior exitosa", op5)

    # 6. Teléfono inválido.
    def op6():
        Cliente("C006", "Sofía Vargas", "sofia.vargas@outlook.com", "310ABC4567")
    ejecutar_operacion(6, "Registro de cliente con teléfono inválido", op6)

    # 7. Cancelación de una reserva confirmada.
    def op7():
        lista_reservas[0].cancelar_reserva()
        return lista_reservas[0].obtener_detalles()
    ejecutar_operacion(7, "Cancelación de una reserva existente", op7)

    # 8. Costo base negativo.
    def op8():
        ReservaSala("S888", -10.0, 10, False)
    ejecutar_operacion(8, "Creación de servicio con costo base negativo", op8)

    # 9. Segunda asesoría exitosa.
    def op9():
        cliente = Cliente("C009", "Valeria Torres", "valeria.torres@yahoo.com", "3112223344")
        servicio = AsesoriaEspecializada("AS02", 150.0, "Base de Datos SQL", False)
        reserva = Reserva("R009", cliente, servicio)
        reserva.procesar_reserva(sesiones=4, bono_calidad=0.0)
        lista_reservas.append(reserva)
        return reserva.obtener_detalles()
    ejecutar_operacion(9, "Segunda asesoría especializada exitosa", op9)

    # 10. Segundo intento de cancelar la reserva ya cancelada en la operación 7.
    def op10():
        lista_reservas[0].cancelar_reserva()
    ejecutar_operacion(10, "Intento de cancelar nuevamente una reserva", op10)

    print("\n" + "=" * 65)
    print("RESUMEN DE LAS DIEZ OPERACIONES")
    print("=" * 65)
    for numero, estado in resultados:
        print(f"Operación {numero:02d}: {estado}")

    correctas = sum(1 for _, estado in resultados if estado == "Correcta")
    fallidas = len(resultados) - correctas
    print(f"\nOperaciones ejecutadas: {len(resultados)}")
    print(f"Operaciones correctas: {correctas}")
    print(f"Errores controlados: {fallidas}")
    print(f"Reservas creadas: {len(lista_reservas)}")
    print("\nDETALLE FINAL DE RESERVAS:")
    for reserva in lista_reservas:
        print(reserva.obtener_detalles())

    logging.info(
        "========== FIN DE LA SIMULACIÓN: %s correctas, %s errores controlados ==========",
        correctas, fallidas
    )
    print(f"\nRegistros guardados en: {LOG_FILE}")
    print("La aplicación finalizó sin detenerse por los errores simulados.")


if __name__ == "__main__":
    ejecutar_simulacion()
