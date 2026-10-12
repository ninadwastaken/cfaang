# flask-api
An example flask rest API server.

To build production, type `make prod`.

To create the env for a new developer, run `make dev_env`.


# Docker Development
With Docker running, build and start the API and MongoDB:

```sh
docker compose up --build
```

Or use the Makefile shortcut:

```sh
make local_build
```

