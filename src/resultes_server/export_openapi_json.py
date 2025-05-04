import json as _jons
import pathlib as _pl

import fastapi.openapi.utils as _fou
import typer as _typer
import typing_extensions as _te

import resultes_server.main as _main

DEFAULT_OUTPUT_FILE_PATH = (
    _pl.Path(__file__).parents[2] / "openapi-schema" / "openapi.json"
)


def export(
    output_file_path: _te.Annotated[
        _pl.Path, _typer.Argument(dir_okay=False, writable=True)
    ] = DEFAULT_OUTPUT_FILE_PATH,
):
    schema = _fou.get_openapi(
        title=_main.app.title,
        version=_main.app.version,
        openapi_version=_main.app.openapi_version,
        description=_main.app.description,
        routes=_main.app.routes,
    )

    with output_file_path.open("w") as output_file:
        _jons.dump(schema, output_file, indent=4)


if __name__ == "__main__":
    _typer.run(export)
