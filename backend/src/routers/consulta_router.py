"""Endpoint 3: consultar la información de un enlace."""

from fastapi import APIRouter, HTTPException, status

from crud.enlace_crud import BaseDatosError
from schemas.enlace_schema import ErrorDetalle, EnlaceInfoResponse
from services import enlace_service

router = APIRouter(prefix="/urls", tags=["Enlaces cortos"])


@router.get(
    "/{short_code}",
    response_model=EnlaceInfoResponse,
    summary="Consultar un enlace",
    responses={404: {"model": ErrorDetalle}, 503: {"model": ErrorDetalle}},
)
def consultar_enlace(short_code: str) -> EnlaceInfoResponse:
    try:
        enlace = enlace_service.obtener_enlace(short_code)
    except enlace_service.EnlaceNoEncontradoError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El enlace corto no existe.") from error
    except BaseDatosError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo consultar la base de datos.") from error

    return EnlaceInfoResponse(short_code=enlace.short_code, original_url=enlace.original_url, created_at=enlace.created_at)
