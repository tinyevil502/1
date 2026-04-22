$mysql = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
& $mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS novel_spider;"
& $mysql -u root -proot novel_spider -e "source D:\project\novel\scripts\init_db.sql"
Write-Host "Database initialized successfully"