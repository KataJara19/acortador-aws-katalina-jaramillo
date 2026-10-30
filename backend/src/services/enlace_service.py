"""Lógica de negocio del acortador.

Aquí se genera el UUID (siempre en el backend), se valida la URL y se
construye el enlace corto. Los routers solo llaman a estas funciones.
"""

import uuid
from datetime import datetime, timezone

from config import get_settings
from crud import enlace_crud
from models.enlace_model import EnlaceCorto
from security.validators import es_codigo_valido, validar_url_original

MAX_INTENTOS = 3


class EnlaceNoEncontradoError(Exception):
    """No existe un enlace con ese short_code."""


def construir_short_url(short_code: str) -> str:
    return f"{get_settings().public_base_url}/{short_code}"


def acortar_url(raw_url: str) -> EnlaceCorto:
    settings = get_settings()
    original_url = validar_url_original(raw_url, settings.max_url_length, settings.public_base_url)

    # Una colisión de UUID v4 es casi imposible, pero se reintenta por seguridad.
    for _ in range(MAX_INTENTOS):
        enlace = EnlaceCorto(
            short_code=str(uuid.uuid4()),
            original_url=original_url,
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        try:
            return enlace_crud.guardar_enlace(enlace)
        except enlace_crud.CodigoDuplicadoError:
            continue
    raise enlace_crud.BaseDatosError("No se pudo generar un código único.")


def obtener_enlace(short_code: str) -> EnlaceCorto:
    # Un código con formato inválido no puede existir: no se consulta la BD.
    if not es_codigo_valido(short_code):
        raise EnlaceNoEncontradoError(short_code)
    enlace = enlace_crud.buscar_enlace(short_code.lower())
    if enlace is None:
        raise EnlaceNoEncontradoError(short_code)
    return enlace
