import json as _jons
import pathlib as _pl

import fastapi.openapi.utils as _fou
import fastapi as _fapi
import typer as _typer
import typing_extensions as _te

import resultes_server.external_server as _ext
import resultes_server.internal_server as _int

_APPS = [("external-server", _ext.app), ("internal-server", _int.app)]

DEFAULT_OUTPUT_DIR_PATH = _pl.Path(__file__).parents[1] / "openapi-schema"


def export(
    output_dir_path: _te.Annotated[
        _pl.Path, _typer.Argument(dir_okay=True, file_okay=False, writable=True)
    ] = DEFAULT_OUTPUT_DIR_PATH,
) -> None:
    for name, app in _APPS:
        _export_app(name, app, output_dir_path)


def _export_app(name: str, app: _fapi.FastAPI, output_dir_path: _pl.Path) -> None:
    schema = _fou.get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    output_file_path = output_dir_path / f"{name}-openapi.json"

    with output_file_path.open("w") as output_file:
        _jons.dump(schema, output_file, indent=4)


if __name__ == "__main__":
    _typer.run(export)
