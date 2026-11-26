"""
PATRÓN 1: STRATEGY (Estrategia)
================================
Idea: definir una familia de algoritmos intercambiables, encapsulando cada uno
en su propia clase, para poder elegir cuál usar en tiempo de ejecución sin
llenar el código de condicionales (if/elif).

Caso de uso: una tienda calcula descuentos distintos según el tipo de cliente.

Flujo agéntico: un agente recibe un OBJETIVO, sigue una lista de PASOS y, tras
ejecutar cada uno, VERIFICA su resultado antes de continuar (ejecutar -> verificar).

Cómo usarlo:
    python patron_1_strategy.py             -> ejecuta el flujo agéntico
    python -m unittest patron_1_strategy -v -> ejecuta las pruebas unitarias
"""
from __future__ import annotations

import unittest
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable


# ---------------------------------------------------------------------------
# 1) ESTRATEGIAS: cada clase es un algoritmo de descuento intercambiable
# ---------------------------------------------------------------------------
class EstrategiaDescuento(ABC):
    """Interfaz común: toda estrategia debe implementar `calcular`."""

    nombre = "base"

    @abstractmethod
    def calcular(self, monto: float) -> float:
        """Devuelve el total a pagar después de aplicar el descuento."""


class SinDescuento(EstrategiaDescuento):
    nombre = "sin descuento"

    def calcular(self, monto: float) -> float:
        return monto  # el cliente paga el monto completo


class DescuentoEstudiante(EstrategiaDescuento):
    nombre = "estudiante (15%)"

    def calcular(self, monto: float) -> float:
        return monto * 0.85  # paga el 85% del monto


class DescuentoTemporada(EstrategiaDescuento):
    nombre = "temporada (25%, tope $500)"

    def calcular(self, monto: float) -> float:
        # El descuento es el 25% del monto, pero nunca puede pasar de $500.
        descuento = min(monto * 0.25, 500)
        return monto - descuento


# ---------------------------------------------------------------------------
# 2) CONTEXTO: usa una estrategia sin conocer los detalles de su algoritmo
# ---------------------------------------------------------------------------
class CarritoCompra:
    def __init__(self, estrategia: EstrategiaDescuento) -> None:
        self.estrategia = estrategia

    def cambiar_estrategia(self, estrategia: EstrategiaDescuento) -> None:
        """Cambia el algoritmo en tiempo de ejecución (núcleo del patrón)."""
        self.estrategia = estrategia

    def total_a_pagar(self, monto: float) -> float:
        # Delega el cálculo en la estrategia actual y redondea a 2 decimales.
        return round(self.estrategia.calcular(monto), 2)


def elegir_estrategia(perfil: str) -> EstrategiaDescuento:
    """Decide qué estrategia usar según el perfil del cliente."""
    catalogo = {
        "estudiante": DescuentoEstudiante(),
        "temporada": DescuentoTemporada(),
    }
    # Si el perfil no existe en el catálogo, se usa la estrategia neutra.
    return catalogo.get(perfil, SinDescuento())


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
                # Si una verificación falla, el agente se detiene.
                print("  ⛔ El agente detuvo el flujo por un error.")
                return False
        return True


def construir_plan(carrito: CarritoCompra, monto: float) -> list[Paso]:
    """Planifica los pasos del caso de uso 'calcular el total de una compra'."""

    def usar_estudiante() -> str:
        carrito.cambiar_estrategia(elegir_estrategia("estudiante"))
        return carrito.estrategia.nombre

    def usar_temporada() -> float:
        carrito.cambiar_estrategia(elegir_estrategia("temporada"))
        return carrito.total_a_pagar(monto)

    return [
        Paso("Elegir la estrategia 'estudiante'",
             usar_estudiante,
             lambda r: r == "estudiante (15%)"),
        Paso("Calcular el total de $1000 con 15% de descuento",
             lambda: carrito.total_a_pagar(monto),
             lambda r: r == 850.0),
        Paso("Cambiar a 'temporada' en tiempo de ejecución",
             usar_temporada,
             lambda r: r == 750.0),
        Paso("Comprobar el tope de $500 con una compra de $5000",
             lambda: carrito.total_a_pagar(5000.0),
             lambda r: r == 4500.0),
        Paso("Un perfil desconocido no recibe descuento",
             lambda: elegir_estrategia("visitante").calcular(monto),
             lambda r: r == 1000.0),
    ]


def main() -> bool:
    carrito = CarritoCompra(SinDescuento())
    agente = AgenteConstructor("Calcular el total con la estrategia adecuada")
    exito = agente.ejecutar_flujo(construir_plan(carrito, 1000.0))
    print("🏁 Resultado:", "TODO CORRECTO" if exito else "HAY ERRORES")
    return exito


# ---------------------------------------------------------------------------
# 4) PRUEBAS UNITARIAS
# ---------------------------------------------------------------------------
class PruebasStrategy(unittest.TestCase):
    def test_cada_estrategia_calcula_bien(self) -> None:
        self.assertEqual(SinDescuento().calcular(200), 200)
        self.assertEqual(DescuentoEstudiante().calcular(200), 170)
        self.assertEqual(DescuentoTemporada().calcular(200), 150)

    def test_descuento_de_temporada_respeta_el_tope(self) -> None:
        self.assertEqual(DescuentoTemporada().calcular(10000), 9500)

    def test_el_carrito_cambia_de_estrategia(self) -> None:
        carrito = CarritoCompra(SinDescuento())
        self.assertEqual(carrito.total_a_pagar(1000), 1000)
        carrito.cambiar_estrategia(DescuentoEstudiante())
        self.assertEqual(carrito.total_a_pagar(1000), 850)

    def test_perfil_desconocido_usa_sin_descuento(self) -> None:
        self.assertIsInstance(elegir_estrategia("otro"), SinDescuento)

    def test_el_agente_completa_el_flujo(self) -> None:
        agente = AgenteConstructor("prueba")
        plan = construir_plan(CarritoCompra(SinDescuento()), 1000.0)
        self.assertTrue(agente.ejecutar_flujo(plan))
        self.assertEqual(len(agente.bitacora), 5)

    def test_el_agente_se_detiene_si_falla_una_verificacion(self) -> None:
        agente = AgenteConstructor("prueba con fallo")
        pasos = [
            Paso("Paso que falla", lambda: 1, lambda r: r == 2),
            Paso("Paso que no debe ejecutarse", lambda: 1, lambda r: True),
        ]
        self.assertFalse(agente.ejecutar_flujo(pasos))
        self.assertEqual(len(agente.bitacora), 1)  # se detuvo en el primero


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
