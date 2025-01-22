from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.models import UserFile, UserFileSchema
from typing import Optional

class UserFileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_file(self, file_name: str, file_zip: bytes) -> UserFile:
        user_file = UserFile(file_name=file_name, file_zip=file_zip)
        self.db.add(user_file)
        await self.db.commit()
        await self.db.refresh(user_file)
        return user_file

    async def get_file(self, file_id: int) -> Optional[UserFile]:
        result = await self.db.execute(select(UserFile).filter(UserFile.id == file_id))
        return result.scalars().first()
