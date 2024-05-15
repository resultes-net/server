from typing import Annotated
import io

from fastapi import FastAPI, File, UploadFile

import pandas as pd

from . import months

app = FastAPI()


@app.post("/profiles/")
async def create_file(
    file: Annotated[UploadFile, File()],
) -> dict:
    data = await file.read()

    bytes_io = io.BytesIO(data)

    df = pd.read_csv(bytes_io, sep="\t")

    total = df["Tot"]
    monthly_total = total[:8761].groupby(months.get_month).sum()

    monthly_values = monthly_total.to_dict()

    return monthly_values
