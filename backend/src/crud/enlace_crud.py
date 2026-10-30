"""Operaciones de acceso a datos (CRUD) sobre la tabla de DynamoDB.

Solo se usan PutItem y GetItem, que son los únicos permisos que concede el
rol IAM de la instancia EC2 (principio de mínimo privilegio).
"""

import logging

from botocore.exceptions import BotoCoreError, ClientError

from database.dynamo_client import get_tabla_enlaces
from models.enlace_model import EnlaceCorto

logger = logging.getLogger("dynamodb")


def _log_error(operation: str, error: Exception) -> None:
    """Registra en la terminal la causa real del fallo de DynamoDB."""
    if isinstance(error, ClientError):
        info = error.response.get("Error", {})
        logger.error("%s falló: %s - %s", operation, info.get("Code"), info.get("Message"))
    else:
        logger.error("%s falló: %s", operation, error)


class BaseDatosError(Exception):
    """Error al comunicarse con DynamoDB."""


class CodigoDuplicadoError(Exception):
    """El short_code ya existe en la tabla (colisión de UUID)."""


def guardar_enlace(enlace: EnlaceCorto) -> EnlaceCorto:
    try:
        get_tabla_enlaces().put_item(
            Item=enlace.to_item(),
            # Nunca sobrescribir un enlace existente.
            ConditionExpression="attribute_not_exists(short_code)",
        )
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            raise CodigoDuplicadoError(enlace.short_code) from error
        _log_error("PutItem", error)
        raise BaseDatosError(str(error)) from error
    except BotoCoreError as error:
        _log_error("PutItem", error)
        raise BaseDatosError(str(error)) from error
    return enlace


def buscar_enlace(short_code: str) -> EnlaceCorto | None:
    try:
        response = get_tabla_enlaces().get_item(Key={"short_code": short_code})
    except (ClientError, BotoCoreError) as error:
        _log_error("GetItem", error)
        raise BaseDatosError(str(error)) from error

    item = response.get("Item")
    return EnlaceCorto.from_item(item) if item else None
