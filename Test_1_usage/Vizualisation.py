import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_excel("water-usage.xlsx")
print(data)
data = data.set_index("Year")
print(data)


plt.plot(data.index, data['Water'])
plt.show()