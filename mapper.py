from sqlalchemy.orm import class_mapper

from models import Properties

mapper = class_mapper(Properties)
#mapper = class_mapper(Client)
#mapper = class_mapper(Users)

for column in mapper.columns:
    print(column.name)

for relationship in mapper.relationships:
    print(relationship.key)
