from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query

from .index import car_make_text_space, car_model_text_space, car_schema, index

query = (
    Query(index)
    .find(car_schema)
    .similar(car_make_text_space.text, Param("make"))
    .similar(car_model_text_space.text, Param("model"))
    .limit(Param("limit"))
)
