

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

df = pd.read_csv("zomato.csv")

df.drop_duplicates(inplace=True)
df.dropna(subset=["rate", "cuisines"], inplace=True)
df = df[df["rate"].str.contains(r'\d', na=False)]
df["rate"] = df["rate"].str.split("/").str[0].astype(float)
df["approx_cost(for two people)"] = (
    df["approx_cost(for two people)"].str.replace(",", "").astype(float)
)


area_ratings = df.groupby("location")["rate"].mean().sort_values(ascending=False).head(10)
area_ratings.plot(kind="barh", figsize=(10,5))
plt.title("Top 10 Locations by Avg Rating")
plt.show()

sns.boxplot(x="online_order", y="rate", data=df)
plt.title("Online Order vs Ratings")
plt.show()

sns.scatterplot(x="approx_cost(for two people)", y="rate", data=df)
plt.title("Cost vs Rating")
plt.show()



