import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


matrices = []
groups = [f'Matrix {i+1}' for i in range(len(matrices))]

# Create DataFrame
data = pd.DataFrame({
    'Value': np.concatenate(matrices),
    'Group': np.repeat(groups, [len(m) for m in matrices])
})

# Plot
plt.figure(figsize=(8, 5))
sns.boxplot(x='Group', y='Value', data=data, palette='pastel')
plt.title("Distributions of Matrices")
plt.xticks(rotation=45)
plt.show()

