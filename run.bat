docker run --name healthDB -p1234:3306 -e MYSQL_ROOT_PASSWORD=healthyboi -d mysql
docker cp healthdb.sql healthDB:healthdb.sql
docker exec -it healthDB mysql -p