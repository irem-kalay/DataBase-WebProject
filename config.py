import os

class Config:
    # General app settings

    # MySQL settings
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '63719403iK')  # Default, change in production
    MYSQL_DB = os.getenv('MYSQL_DB', 'imdb2')
    MYSQL_CURSORCLASS = 'DictCursor'



    # burayi degisince gitignore dan dolayi digerlerini etkilemicek