$mysqlPath = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
$sqlFile = "$PSScriptRoot\init_db.sql"
& $mysqlPath -u root -proot -e "source $sqlFile"