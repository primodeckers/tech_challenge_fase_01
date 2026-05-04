"""Pandera: checagem do nome das colunas numa linha de predição."""

from __future__ import annotations

import pandera.pandas as pa


def feature_row_schema(columns: list[str]) -> pa.DataFrameSchema:
    """Uma linha tem de trazer só estas colunas (strict); ordem tanto faz."""
    return pa.DataFrameSchema(
        {c: pa.Column() for c in columns},
        strict=True,
        coerce=False,
    )
