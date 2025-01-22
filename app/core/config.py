import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:root_password@db-frame-extractor:3306/frame_extractor"
)
