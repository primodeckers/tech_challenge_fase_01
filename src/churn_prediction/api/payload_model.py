"""Modelo Pydantic dinâmico para POST /predict — espelha colunas do artefacto (extra proibido)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, create_model


def build_churn_row_model(columns: list[str]) -> type[BaseModel]:
    """Uma feature por campo; `alias` preserva nomes com espaço (ex.: \"Zip Code\")."""
    fields: dict[str, Any] = {}
    for i, col in enumerate(columns):
        fname = f"f{i}"
        fields[fname] = (
            Any,
            Field(alias=col),
        )
    return create_model(
        "ChurnRowPayload",
        __base__=BaseModel,
        __config__=ConfigDict(extra="forbid"),
        **fields,
    )
