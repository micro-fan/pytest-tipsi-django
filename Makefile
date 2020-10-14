test_db:
	POSTGRES_PASSWORD=password docker run -d -p 40001:5432 --name=testpostgres --rm=true postgres
	sleep 15
	echo create database plugin | PGPASSWORD=password psql -h localhost -p 40001 -U postgres

tox_test:
	tox -e py38 -- -vsx --docker-skip
