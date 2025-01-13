import dataclasses as _dc

import fastapi as _fapi

PredefinedProfileName = str


@_dc.dataclass
class Demand:
    profile: PredefinedProfileName | _fapi.UploadFile
