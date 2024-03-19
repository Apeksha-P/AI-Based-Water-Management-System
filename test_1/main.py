import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid", {'axes.facecolor': '#1A1F35'})

data = pd.read_excel("water-usage.xlsx")
data = data.set_index("Days")
print(data)

plt.bar(data.index, data['Water'],color='#0E3653', width=0.95)
plt.xlabel("Days")
plt.ylabel("Water(L)")
plt.title("VISUALIZING FUTURE WATER USAGE TREND FOR COMING UP DAYS")
plt.xticks(rotation=45)  
plt.show()






