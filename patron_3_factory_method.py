"""
PATRÓN 3: FACTORY METHOD (Método Fábrica)
==========================================
Idea: delegar la creación de objetos a una fábrica, para que el código cliente
no dependa de las clases concretas. Así se pueden agregar productos nuevos sin
modificar el código que ya existe.

Caso de uso: generar reportes en distintos formatos (texto, HTML, CSV y, luego,
markdown) a partir de los mismos datos.

Flujo agéntico: el agente pide formatos a la fábrica y VERIFICA cada salida.

Cómo usarlo:
    python patron_3_factory_method.py             -> ejecuta el flujo agéntico
    python -m unittest patron_3_factory_method -v -> ejecuta las pruebas unitarias
"""
from __future__ import annotations

import unittest
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable


# ---------------------------------------------------------------------------
# 1) PRODUCTOS: cada reporte concreto sabe generarse en su formato
# ---------------------------------------------------------------------------
class Reporte(ABC):
    """Producto abstracto: todos los reportes comparten esta interfaz."""

    @abstractmethod
    def generar(self, titulo: str, filas: list[tuple]) -> str:
        """Devuelve el reporte como texto en el formato correspondiente."""


class ReporteTexto(Reporte):
    def generar(self, titulo: str, filas: list[tuple]) -> str:
        lineas = [titulo.upper(), "-" * len(titulo)]  # título subrayado
        lineas += [f"{nombre}: {valor}" for nombre, valor in filas]
        return "\n".join(lineas)


class ReporteHTML(Reporte):
    def generar(self, titulo: str, filas: list[tuple]) -> str:
        elementos = "".join(f"<li>{n}: {v}</li>" for n, v in filas)
        return f"<h1>{titulo}</h1><ul>{elementos}</ul>"


class ReporteCSV(Reporte):
    def generar(self, titulo: str, filas: list[tuple]) -> str:
        # El CSV no lleva título: solo encabezado y filas de datos.
        return "\n".join(["nombre,valor"] + [f"{n},{v}" for n, v in filas])


# ---------------------------------------------------------------------------
# 2) FÁBRICA: decide qué clase concreta crear según el formato pedido
# ---------------------------------------------------------------------------
class FabricaReportes:
    _formatos: dict[str, type[Reporte]] = {
        "texto": ReporteTexto,
        "html": ReporteHTML,
        "csv": ReporteCSV,
    }

    @classmethod
    def crear(cls, formato: str) -> Reporte:
        """Devuelve un reporte del formato pedido (sin importar mayúsculas)."""
        clase = cls._formatos.get(formato.lower())
        if clase is None:
            raise ValueError(f"Formato no soportado: {formato}")
        return clase()

    @classmethod
    def registrar(cls, formato: str, clase: type[Reporte]) -> None:
        """Agrega un formato nuevo sin modificar el código existente."""
        cls._formatos[formato.lower()] = clase

    @classmethod
    def eliminar(cls, formato: str) -> None:
        """Quita un formato (útil para dejar limpia la fábrica en las pruebas)."""
        cls._formatos.pop(formato.lower(), None)


class ReporteMarkdown(Reporte):
    """Formato nuevo, definido DESPUÉS para demostrar la extensibilidad."""

    def generar(self, titulo: str, filas: list[tuple]) -> str:
        return f"# {titulo}\n" + "\n".join(f"- **{n}**: {v}" for n, v in filas)


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
            vista = repr(resultado)
            if len(vista) > 60:                          # acorta salidas largas
                vista = vista[:57] + "..."
            icono = "✅" if correcto else "❌"
            print(f"  {icono} Paso {numero}: {paso.descripcion} -> {vista}")
            if not correcto:
                print("  ⛔ El agente detuvo el flujo por un error.")
                return False
        return True


DATOS_EJEMPLO = [("Aprobados", 25), ("Reprobados", 3)]


def construir_plan() -> list[Paso]:
    """Planifica los pasos del caso de uso 'generar reportes en varios formatos'."""

    def formato_invalido() -> bool:
        try:
            FabricaReportes.crear("pdf")
            return False                        # no debió aceptarlo
        except ValueError:
            return True

    def registrar_y_crear_markdown() -> str:
        FabricaReportes.registrar("markdown", ReporteMarkdown)
        return FabricaReportes.crear("markdown").generar("Resumen", DATOS_EJEMPLO)

    return [
        Paso("Crear reporte de texto",
             lambda: FabricaReportes.crear("texto").generar("Resumen", DATOS_EJEMPLO),
             lambda r: r.startswith("RESUMEN") and "Aprobados: 25" in r),
        Paso("Crear reporte HTML",
             lambda: FabricaReportes.crear("html").generar("Resumen", DATOS_EJEMPLO),
             lambda r: r.startswith("<h1>Resumen</h1>") and r.count("<li>") == 2),
        Paso("Crear reporte CSV",
             lambda: FabricaReportes.crear("csv").generar("Resumen", DATOS_EJEMPLO),
             lambda r: r.splitlines()[0] == "nombre,valor" and len(r.splitlines()) == 3),
        Paso("Rechazar un formato desconocido (pdf)",
             formato_invalido, lambda r: r is True),
        Paso("Registrar un formato nuevo (markdown) y usarlo",
             registrar_y_crear_markdown, lambda r: r.startswith("# Resumen")),
    ]


def main() -> bool:
    agente = AgenteConstructor("Generar un reporte en varios formatos con una fábrica")
    exito = agente.ejecutar_flujo(construir_plan())
    FabricaReportes.eliminar("markdown")  # deja la fábrica como estaba
    print("🏁 Resultado:", "TODO CORRECTO" if exito else "HAY ERRORES")
    return exito


# ---------------------------------------------------------------------------
# 4) PRUEBAS UNITARIAS
# ---------------------------------------------------------------------------
class PruebasFactoryMethod(unittest.TestCase):
    def tearDown(self) -> None:
        FabricaReportes.eliminar("markdown")  # evita que una prueba afecte a otra

    def test_la_fabrica_crea_la_clase_correcta(self) -> None:
        self.assertIsInstance(FabricaReportes.crear("texto"), ReporteTexto)
        self.assertIsInstance(FabricaReportes.crear("html"), ReporteHTML)
        self.assertIsInstance(FabricaReportes.crear("csv"), ReporteCSV)

    def test_el_formato_no_distingue_mayusculas(self) -> None:
        self.assertIsInstance(FabricaReportes.crear("HTML"), ReporteHTML)

    def test_formato_desconocido_lanza_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "Formato no soportado"):
            FabricaReportes.crear("pdf")

    def test_cada_formato_genera_su_salida(self) -> None:
        self.assertEqual(
            FabricaReportes.crear("csv").generar("T", [("a", 1)]), "nombre,valor\na,1")
        self.assertEqual(
            FabricaReportes.crear("html").generar("T", [("a", 1)]),
            "<h1>T</h1><ul><li>a: 1</li></ul>")

    def test_se_puede_registrar_un_formato_nuevo(self) -> None:
        FabricaReportes.registrar("markdown", ReporteMarkdown)
        salida = FabricaReportes.crear("markdown").generar("T", [("a", 1)])
        self.assertEqual(salida, "# T\n- **a**: 1")

    def test_el_agente_completa_el_flujo(self) -> None:
        agente = AgenteConstructor("prueba")
        self.assertTrue(agente.ejecutar_flujo(construir_plan()))
        self.assertEqual(len(agente.bitacora), 5)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
