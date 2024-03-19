import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv("quality.csv")
data = data.set_index("Date")
print(data)

plt.plot(data.index,data['ph'])
plt.show()




