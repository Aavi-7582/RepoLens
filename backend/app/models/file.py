from sqlalchemy import Column, Integer, String, Text, ForeignKey

from app.core.database import Base


class RepositoryFile(Base):
    __tablename__ = "repository_files"

    id = Column(Integer, primary_key=True, index=True)

    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False
    )

    file_path = Column(String, nullable=False)
    language = Column(String, nullable=True)
    content = Column(Text, nullable=False)