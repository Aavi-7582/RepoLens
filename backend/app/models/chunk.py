from sqlalchemy import Column, Integer, String, Text, ForeignKey

from app.core.database import Base


class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id = Column(Integer, primary_key=True, index=True)

    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False
    )

    file_id = Column(
        Integer,
        ForeignKey("repository_files.id"),
        nullable=False
    )

    file_path = Column(String, nullable=False)
    language = Column(String, nullable=True)

    chunk_type = Column(String, nullable=True)
    symbol_name = Column(String, nullable=True)

    content = Column(Text, nullable=False)