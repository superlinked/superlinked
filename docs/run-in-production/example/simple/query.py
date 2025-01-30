from superlinked import framework as sl

from .index import car_make_text_space, car_model_text_space, car_schema, index

query = (
    sl.Query(index)
    .find(car_schema)
    .similar(car_make_text_space.text, sl.Param("make"))
    .similar(car_model_text_space.text, sl.Param("model"))
    .select_all()
    .limit(sl.Param("limit"))
)
