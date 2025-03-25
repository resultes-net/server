FROM postgres:17.4-bookworm

WORKDIR /app

COPY alembic/upgrade.sql alembic/upgrade.sql

RUN psql -U $POSTGRES_USER $POSTGRES_DB < upgrade.sql

CMD ["postgres"]
