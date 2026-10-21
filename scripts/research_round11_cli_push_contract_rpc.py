import inspect
import json
from kaggle.api.kaggle_api_extended import KaggleApi
print(json.dumps({'CLI_wrapper':inspect.getsource(KaggleApi.kernels_push_cli)[:12000]}))
