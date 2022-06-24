import json
from matplotlib.font_manager import json_load
import pandas as pd

datas = {"신차가격": [1000, 900, 800, 700, 600, 500], "중고": [800, 700, 600, 500]}
datas = json.loads(datas)

for i, v in enumerate(datas):

    if v['신차가격'] == 1000:
        del datas[i]
        continue

    if v['중고가격'] == 700:
        del datas[i]
        continue

    if v['신차가격'] == 800:
        del datas[i]
        continue

print(datas)
