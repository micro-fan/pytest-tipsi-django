test_db:
	docker run -d -p 40001:5432 --name=testpostgres --rm=true postgres
	sleep 15
	echo create database plugin | psql -h localhost -p 40001 -U postgres

tox_test:
	tox -e py36 -- -vsx --docker-skip
