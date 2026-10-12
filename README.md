# flask-api
An example flask rest API server.

To build production, type `make prod`.

To create the env for a new developer, run `make dev_env`.


# Docker Development
With Docker running, build and start the API and MongoDB:

```sh
make local_build
```

then to load data into MongoDB run: 

```sh
make local_db
```

View MongoDB Logs: 

```sh
docker compose logs --tail=50 -f mongo
```

Open MongoDB shell for querying:
```sh
docker compose exec mongo mongosh
```