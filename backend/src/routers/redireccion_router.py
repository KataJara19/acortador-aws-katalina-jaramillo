"""Endpoint 2: redirigir al destino original.

Este router se registra al final en main.py porque su ruta /{short_code}
captura cualquier segmento y no debe ocultar /health, /urls o /docs.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from crud.enlace_crud import BaseDatosError
from schemas.enlace_schema import ErrorDetalle
from services import enlace_service

router = APIRouter(tags=["Redirección"])


@router.get(
    "/{short_code}",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_class=RedirectResponse,
    summary="Redirigir a la URL original",
    responses={404: {"model": ErrorDetalle}, 503: {"model": ErrorDetalle}},
)
def redirigir_a_original(short_code: str) -> RedirectResponse:
    try:
        enlace = enlace_service.obtener_enlace(short_code)
    except enlace_service.EnlaceNoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El enlace corto no existe.") from error
    except BaseDatosError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo consultar la base de datos.") from error

    # Redirección HTTP real: el navegador navega solo hacia la URL original.
    return RedirectResponse(
        url=enlace.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        headers={"Cache-Control": "no-store"},
    )
