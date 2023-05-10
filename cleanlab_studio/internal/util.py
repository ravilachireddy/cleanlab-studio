import pathlib
from typing import Any, Optional, TypeVar, Union

import numpy as np
import pandas as pd

try:
    import pyspark.sql

    pyspark_exists = True
except ImportError:
    pyspark_exists = False

from .dataset_source import (
    DatasetSource,
    FilepathDatasetSource,
    PandasDatasetSource,
)

dataset_source_types = (
    Union[str, pathlib.Path, pd.DataFrame]
    if not pyspark_exists
    else Union[str, pathlib.Path, pd.DataFrame, pyspark.sql.DataFrame]
)

DatasetSourceType = TypeVar("DatasetSourceType", bound=dataset_source_types)  # type: ignore


def init_dataset_source(
    dataset_source: DatasetSourceType, dataset_name: Optional[str] = None
) -> DatasetSource:
    if isinstance(dataset_source, pd.DataFrame):
        if dataset_name is None:
            raise ValueError("Must provide dataset name if uploading from a DataFrame")
        return PandasDatasetSource(df=dataset_source, dataset_name=dataset_name)
    elif isinstance(dataset_source, pathlib.Path):
        return FilepathDatasetSource(filepath=dataset_source, dataset_name=dataset_name)
    elif isinstance(dataset_source, str):
        return FilepathDatasetSource(
            filepath=pathlib.Path(dataset_source), dataset_name=dataset_name
        )
    elif pyspark_exists and isinstance(dataset_source, pyspark.sql.DataFrame):
        from .dataset_source import PySparkDatasetSource

        if dataset_name is None:
            raise ValueError("Must provide dataset name if uploading from a DataFrame")
        return PySparkDatasetSource(df=dataset_source, dataset_name=dataset_name)
    else:
        raise ValueError("Invalid dataset source provided")


def as_numpy_type(field_type: str) -> Any:
    return {
        "string": str,
        "integer": np.int64,  # XXX backend might use big integers
        "float": np.float64,
        "boolean": bool,
    }[field_type]