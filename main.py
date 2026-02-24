#!/usr/bin/env python3
"""
main.py – Punto de entrada del proyecto
--------------------------------------
* Compatibilidad: Linux (Kali, Ubuntu, etc.)
* Requiere Python 3.8+
* Usa `argparse` para la línea de comandos
* Incluye un logger básico
* Estructura preparada para pruebas unitarias
"""

import argparse
import logging
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Configuración del logger
# ----------------------------------------------------------------------
def setup_logger(verbose: bool = False) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    logging.basicConfig(level=level, format=fmt, stream=sys.stdout)
    return logging.getLogger(Path(__file__).stem)


# ----------------------------------------------------------------------
# Funciones del proyecto (rellenar según la lógica del negocio)
# ----------------------------------------------------------------------
def do_something(input_file: Path, output_dir: Path) -> None:
    """
    Ejemplo: leer `input_file`, procesar datos y escribir resultados
    en `output_dir`.
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"Procesando {input_file} → {output_dir}")

    # --- TODO: lógica del proyecto ---
    # with input_file.open('r') as f:
    #     data = f.read()
    # result = proceso(data)
    # (output_dir / "resultado.txt").write_text(result)
    # -------------------------------------------------


# ----------------------------------------------------------------------
# Parser de argumentos
# ----------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Herramienta principal del proyecto",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Archivo de entrada (ej. datos.txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path.cwd(),
        help="Directorio donde se guardarán los resultados",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Muestra información de depuración",
    )
    return parser


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logger = setup_logger(args.verbose)
    logger.info("Inicio del programa")
    logger.debug(f"Args: {args}")

    try:
        do_something(args.input, args.output)
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        return 1

    logger.info("Fin del programa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
