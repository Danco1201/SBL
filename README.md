# SBL - Stack Based Language

## Descripción
SBL (*Stack Based Language*) es un lenguaje de programación de bajo nivel basado en el uso de una pila, aunque tambien incluye concurrencia y modularidad. Diseñado para programadores que buscan un control detallado sobre los procesos, SBL permite explorar conceptos fundamentales de la computación y aprender cómo interactuar directamente con estructuras como pilas, variables y flujos de control.

---

## Características
- **Operaciones con pilas:** `PUSH`, `POP`, `TOP`, operaciones matemáticas y lógicas basadas en la pila.
- **Control de flujo:** `WHILE`, `ENDWHILE`, bucles y saltos condicionales.
- **Variables:** Soporte básico para almacenar y recuperar valores.
- **Concurrencia:** Crear y manejar múltiples hilos con `THREAD` y `JOIN`.
- **Modularidad:** Incluir y usar módulos externos con `INCLUDE`.
- **Funciones lambda:** Manejo de funciones anonimas con `LAMBDA` y llamada de funciones anonimas con `FLAMBDA`
- **Funciones como etiquetas:** Llamada de funciones con `CALL` y las funciones son tratadas como etiquetas
- **Arreglos:** Manejo de arrays con `ARRCREATE`, `ARRSET` y `ARRGET`
- **P.O.O. en bajo nivel:** Programacion orientada objetos con instrucciones similares a las de la maquina, como `CREATE`, `CLASS`, `SETATTR` y `GETATTR`
- **Manejo de memoria:** Manejo de memoria con `MALLOC` y `FREE`
- **Strings:** Manejo de cadenas com `CONCAT` para concatenar y `SUBSTRING` para subcadenas
- **Operaciones con pilas avanzadas:** `CLEAR`, `SIZE`, `EMPTY`, etc.

---

## Requisitos
- Python 3.11 o superior.

---

## Cómo usar
1. Clona este repositorio:
   ```git
   git clone https://github.com/Danco1201/SBL.git
   cd sbl
2. Escribe un archivo SBL. Ejemplo: `file.sbl`:
   ```sbl
   SET x 5
   LAMBDA func x + 5
   PUSH 10
   PRINT "El resultado es:"
   GET x
   CALL func
   ADD
   PRINT "Fin del programa."
3. Ejecuta el interprete:
   ```bash
   python interpreter.py file.sbl

## Estructura del proyecto:
- `interprete.py`: El unico archivo. Maneja todo el interprete. Modificar con precaucion

## ADVERTENCIAS
El lenguaje no esta listo, asi que es probable que tenga muchos errores. Si encuentran uno, hagan una pull request o avisenme
