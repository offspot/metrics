from humps import camelize
from pydantic import BaseModel, ConfigDict


class CamelModel(BaseModel):
    """Model than transform Python snake_case into JSON camelCase"""

    model_config = ConfigDict(alias_generator=camelize, populate_by_name=True)
