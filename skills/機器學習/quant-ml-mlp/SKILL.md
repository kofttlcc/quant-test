name: mlp-timeseries-forecasting 
description: 構建專用於金融時間序列預測的 MLP 模型，包含實體嵌入 (Entity Embeddings) 與特徵歸一化層。

MLP 模型架構技能指令
你是一名深度學習工程師。請設計一個能夠處理混合數據（連續值 + 類別值）的 MLP 架構 。

1. 輸入層處理
1.1 連續特徵 (Continuous): 直接輸入，但在送入模型前必須進行標準化 (Z-score) 或 歸一化 (MinMax)。注意： 參數 scaler 只能由訓練集擬合。
1.2 類別特徵 (Categorical): 如 DayOfWeek, Sector。禁止使用 One-Hot Encoding。必須使用 Entity Embedding 層將其映射為低維稠密向量，以捕捉類別間的語義關係。

2. 網絡結構
2.1 Dropout: 在每個 Dense 層後添加 Dropout (0.2-0.5) 以防止過擬合（金融數據噪聲大）。
2.2 激活函數: 使用 ReLU 或 Leaky ReLU。
2.3 輸出層:
- 回歸任務：Linear (1 unit).
- 二分類任務（漲/跌）：Sigmoid (1 unit).

3. 代碼結構 (Keras/TensorFlow)python
from tensorflow.keras.layers import Input, Dense, Embedding, Concatenate, Dropout from tensorflow.keras.models import Model

def build_mlp(n_continuous, cat_info):  # cat_info: list of (n_categories, embed_dim)

# 連續輸入
input_cont = Input(shape=(n_continuous,))

# 類別輸入與嵌入
inputs = [input_cont]
embeddings =
for n_cat, dim in cat_info:
    inp = Input(shape=(1,))
    emb = Embedding(n_cat, dim)(inp)
    emb = Flatten()(emb)
    inputs.append(inp)
    embeddings.append(emb)

# 拼接
x = Concatenate()([input_cont] + embeddings)
x = Dense(64, activation='relu')(x)
x = Dropout(0.3)(x)
output = Dense(1)(x)

return Model(inputs, output)