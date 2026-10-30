"""Endpoint 1: crear un enlace corto."""

from fastapi import APIRouter, HTTPException, status

from crud.enlace_crud import BaseDatosError
from schemas.enlace_schema import ErrorDetalle, AcortarRequest, AcortarResponse
from security.validators import UrlInvalidaError
from services import enlace_service

router = APIRouter(tags=["Enlaces cortos"])


@router.post(
    "/shorten",
    response_model=AcortarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un enlace corto",
    responses={422: {"model": ErrorDetalle}, 503: {"model": ErrorDetalle}},
)
def crear_enlace_corto(payload: AcortarRequest) -> AcortarResponse:
    try:
        enlace = enlace_service.acortar_url(payload.original_url)
    except UrlInvalidaError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)) from error
    except BaseDatosError as error:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo guardar el enlace en la base de datos."
        ) from error

    return AcortarResponse(
        short_code=enlace.short_code,
        original_url=enlace.original_url,
        short_url=enlace_service.construir_short_url(enlace.short_code),
    )
