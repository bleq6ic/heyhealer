import pandas as pd
import json



datas = []
data = {"brand":"현대","model_group":"i30","model":"i30 PD","grade":"좋은 등급","years":2010}
data2 = {"brand":"기아","model_group":"스포티지","model":"티지 PD","grade":"안좋은 등급","years":2015}
data3 = {"brand":"BMW","model_group":"BMWi","model":" PD","grade":"중간 등급","years":2000}
data3 = {"brand":"벤츠","model_group":"c클","model":" 220","grade":"중간 등급","years":2000}
datas.append(data)
datas.append(data2)
datas.append(data3)

for i, v in enumerate(datas):
    if v['brand'] == "기아":
        del datas[i]
        continue

    if v['brand'] == "BMW":
        del datas[i]
        continue

print(datas)
df_datas = pd.DataFrame(datas)

sort_datas = df_datas.sort_values('years')
print(sort_datas)

dict_datas = sort_datas.to_dict('records')
print(dict_datas)