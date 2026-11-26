"""
PATRÓN 2: OBSERVER (Observador)
================================
Idea: un objeto (el sujeto) avisa automáticamente a varios observadores cuando
cambia su estado, sin acoplarse a ninguno de ellos. Se pueden agregar o quitar
observadores sin modificar al sujeto.

Caso de uso: un ticket de soporte técnico cambia de estado y se notifica al
estudiante (correo), al historial (registro) y al panel del técnico.

Flujo agéntico: el agente suscribe observadores, dispara cambios de estado y
VERIFICA que cada observador reaccionó como se esperaba.

Cómo usarlo:
    python patron_2_observer.py             -> ejecuta el flujo agéntico
    python -m unittest patron_2_observer -v -> ejecuta las pruebas unitarias
"""
from __future__ import annotations

import unittest
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable


# ---------------------------------------------------------------------------
# 1) OBSERVADORES: cada uno reacciona a su manera al mismo aviso
# ---------------------------------------------------------------------------
class Observador(ABC):
    """Interfaz: cualquier observador debe saber reaccionar a un cambio."""

    @abstractmethod
    def actualizar(self, ticket_id: int, nuevo_estado: str) -> None:
        """Se invoca automáticamente cuando el ticket cambia de estado."""


class NotificadorCorreo(Observador):
    def __init__(self) -> None:
        self.correos_enviados: list[str] = []

    def actualizar(self, ticket_id: int, nuevo_estado: str) -> None:
        # En un sistema real aquí se enviaría un correo; simulamos guardándolo.
        self.correos_enviados.append(f"Ticket #{ticket_id} ahora está: {nuevo_estado}")


class Historial(Observador):
    def __init__(self) -> None:
        self.registros: list[tuple[int, str]] = []

    def actualizar(self, ticket_id: int, nuevo_estado: str) -> None:
        self.registros.append((ticket_id, nuevo_estado))  # deja constancia


class PanelTecnico(Observador):
    def __init__(self) -> None:
        self.pendientes = 0  # tickets abiertos que aún no se resuelven

    def actualizar(self, ticket_id: int, nuevo_estado: str) -> None:
        if nuevo_estado == "abierto":
            self.pendientes += 1
        elif nuevo_estado == "resuelto":
            self.pendientes -= 1


# ---------------------------------------------------------------------------
# 2) SUJETO: mantiene la lista de suscriptores y los avisa de cada cambio
# ---------------------------------------------------------------------------
class Ticket:
    ESTADOS_VALIDOS = ("abierto", "en proceso", "resuelto")

    def __init__(self, ticket_id: int) -> None:
        self.ticket_id = ticket_id
        self.estado = "nuevo"
        self._observadores: list[Observador] = []

    def suscribir(self, observador: Observador) -> None:
        self._observadores.append(observador)

    def desuscribir(self, observador: Observador) -> None:
        self._observadores.remove(observador)

    def cambiar_estado(self, nuevo_estado: str) -> None:
        # Validamos antes de cambiar, para no avisar de estados inexistentes.
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {nuevo_estado}")
        self.estado = nuevo_estado
        # Notificación: se avisa a todos los suscriptores, en orden.
        for observador in self._observadores:
            observador.actualizar(self.ticket_id, nuevo_estado)

    def cantidad_observadores(self) -> int:
        return len(self._observadores)


# ---------------------------------------------------------------------------
# 3) AGENTE: construye y comprueba el caso de uso paso a paso
# ---------------------------------------------------------------------------
@dataclass
class Paso:
    """Un paso del plan: qué hacer y cómo comprobar que salió bien."""

    descripcion: str
    accion: Callable[[], Any]
    verificacion: Callable[[Any], bool]


class AgenteConstructor:
    """Agente que ejecuta un plan, verifica cada paso y guarda una bitácora."""

    def __init__(self, objetivo: str) -> None:
        self.objetivo = objetivo
        self.bitacora: list[tuple[str, Any, bool]] = []

    def ejecutar_flujo(self, pasos: list[Paso]) -> bool:
        print(f"\n🎯 Objetivo: {self.objetivo}")
        for numero, paso in enumerate(pasos, start=1):
            resultado = paso.accion()                    # EJECUTAR
            correcto = paso.verificacion(resultado)      # VERIFICAR
            self.bitacora.append((paso.descripcion, resultado, correcto))
            icono = "✅" if correcto else "❌"
            print(f"  {icono} Paso {numero}: {paso.descripcion} -> {resultado}")
            if not correcto:
                print("  ⛔ El agente detuvo el flujo por un error.")
                return False
        return True


def construir_plan(ticket: Ticket, correo: NotificadorCorreo,
                   historial: Historial, panel: PanelTecnico) -> list[Paso]:
    """Planifica los pasos del caso de uso 'seguir la vida de un ticket'."""

    def suscribir_todos() -> int:
        for observador in (correo, historial, panel):
            ticket.suscribir(observador)
        return ticket.cantidad_observadores()

    def abrir() -> int:
        ticket.cambiar_estado("abierto")
        return panel.pendientes

    def poner_en_proceso() -> int:
        ticket.cambiar_estado("en proceso")
        return len(historial.registros)

    def quitar_correo_y_resolver() -> int:
        ticket.desuscribir(correo)             # el correo deja de recibir avisos
        ticket.cambiar_estado("resuelto")
        return len(correo.correos_enviados)    # no debe haber recibido el último

    def probar_estado_invalido() -> bool:
        try:
            ticket.cambiar_estado("volando")
            return False                       # no debió aceptarlo
        except ValueError:
            return True

    return [
        Paso("Suscribir 3 observadores", suscribir_todos, lambda r: r == 3),
        Paso("Cambiar a 'abierto' (el panel cuenta 1 pendiente)",
             abrir, lambda r: r == 1),
        Paso("Cambiar a 'en proceso' (el historial guarda 2 registros)",
             poner_en_proceso, lambda r: r == 2),
        Paso("Desuscribir el correo y resolver (correo se queda en 2 avisos)",
             quitar_correo_y_resolver, lambda r: r == 2),
        Paso("El panel quedó sin pendientes",
             lambda: panel.pendientes, lambda r: r == 0),
        Paso("Rechazar un estado inválido",
             probar_estado_invalido, lambda r: r is True),
    ]


def main() -> bool:
    ticket = Ticket(ticket_id=101)
    agente = AgenteConstructor("Notificar automáticamente los cambios de un ticket")
    plan = construir_plan(ticket, NotificadorCorreo(), Historial(), PanelTecnico())
    exito = agente.ejecutar_flujo(plan)
    print("🏁 Resultado:", "TODO CORRECTO" if exito else "HAY ERRORES")
    return exito


# ---------------------------------------------------------------------------
# 4) PRUEBAS UNITARIAS
# ---------------------------------------------------------------------------
class PruebasObserver(unittest.TestCase):
    def setUp(self) -> None:
        self.ticket = Ticket(7)
        self.historial = Historial()
        self.ticket.suscribir(self.historial)

    def test_el_observador_recibe_cada_cambio(self) -> None:
        self.ticket.cambiar_estado("abierto")
        self.ticket.cambiar_estado("resuelto")
        self.assertEqual(self.historial.registros, [(7, "abierto"), (7, "resuelto")])

    def test_varios_observadores_reciben_el_mismo_aviso(self) -> None:
        correo = NotificadorCorreo()
        self.ticket.suscribir(correo)
        self.ticket.cambiar_estado("abierto")
        self.assertEqual(correo.correos_enviados, ["Ticket #7 ahora está: abierto"])
        self.assertEqual(len(self.historial.registros), 1)

    def test_un_observador_desuscrito_ya_no_recibe_avisos(self) -> None:
        self.ticket.desuscribir(self.historial)
        self.ticket.cambiar_estado("abierto")
        self.assertEqual(self.historial.registros, [])

    def test_estado_invalido_no_notifica_ni_cambia_el_estado(self) -> None:
        with self.assertRaises(ValueError):
            self.ticket.cambiar_estado("volando")
        self.assertEqual(self.ticket.estado, "nuevo")
        self.assertEqual(self.historial.registros, [])

    def test_el_panel_cuenta_pendientes(self) -> None:
        panel = PanelTecnico()
        self.ticket.suscribir(panel)
        self.ticket.cambiar_estado("abierto")
        self.assertEqual(panel.pendientes, 1)
        self.ticket.cambiar_estado("resuelto")
        self.assertEqual(panel.pendientes, 0)

    def test_el_agente_completa_el_flujo(self) -> None:
        agente = AgenteConstructor("prueba")
        plan = construir_plan(Ticket(1), NotificadorCorreo(), Historial(), PanelTecnico())
        self.assertTrue(agente.ejecutar_flujo(plan))
        self.assertEqual(len(agente.bitacora), 6)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
