# Flujo de construcción agéntica: 3 patrones de diseño en Python

Tres archivos independientes, sin dependencias externas (solo Python 3.9+).
Cada uno implementa **un patrón de diseño** con un **caso de uso** y un
**flujo agéntico**: un agente recibe un objetivo, ejecuta una lista de pasos y
**verifica** cada resultado; si una verificación falla, se detiene.

| Archivo | Patrón | Caso de uso |
|---|---|---|
| `patron_1_strategy.py` | Strategy | Descuentos intercambiables según el tipo de cliente |
| `patron_2_observer.py` | Observer | Un ticket de soporte avisa a correo, historial y panel técnico |
| `patron_3_factory_method.py` | Factory Method | Reportes en texto, HTML, CSV y un formato nuevo (markdown) |

## Ejecutar el flujo agéntico

```
py patron_1_strategy.py
py patron_2_observer.py
py patron_3_factory_method.py
```

## Ejecutar las pruebas unitarias

```
py -m unittest patron_1_strategy patron_2_observer patron_3_factory_method -v
```

