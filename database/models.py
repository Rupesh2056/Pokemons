from sqlalchemy import Column, Integer, String, Table, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

#  table to represent the many-to-many relationship (Pokemon and types)
pokemon_type_association = Table(
    "pokemon_type_association",
    Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemon.id")),
    Column("type_id", Integer, ForeignKey("type.id")),
)

class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    image = Column(String)

     # relationship to "Type" using the association table
    types = relationship("Type", secondary=pokemon_type_association, back_populates="pokemons")


class Type(Base):
    __tablename__ = "type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # reverse relationship to "Pokemon"
    pokemons = relationship("Pokemon", secondary=pokemon_type_association, back_populates="types")


# table to track what datas has already been fetched and what phases are yet to be fetched
class FetchPhaseInfo(Base):
    __tablename__ = "fetch_info"

    id = Column(Integer,primary_key=True)
    phase_1_complete = Column(Boolean, unique=False, default=False)
    phase_2_complete = Column(Boolean, unique=False, default=False)
    phase_3_complete = Column(Boolean, unique=False, default=False)
    phase_4_complete = Column(Boolean, unique=False, default=False)
    phase_5_complete = Column(Boolean, unique=False, default=False)
