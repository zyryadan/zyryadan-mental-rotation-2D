import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

'''
Function to compare human and AI
Usage: python cognitive_efficiency.py
'''

#DATA ENTRY
human_data = {
    'Group': ['Human'] * 10,
    'Time_Per_Task': [41.52, 57.36, 47.84, 63.01, 24.45, 36.93, 15.11, 87.55, 25.50, 40.33],
    'Accuracy': [1.00, 0.70, 0.70, 0.90, 0.50, 0.80, 0.73, 1.00, 0.70, 0.60]
}

ai_gemini3_data = {
    'Group': ['AI_Gemini_3 (Pro/Flash)'] * 8,
    'Time_Per_Task': [101.49, 110.47, 63.71, 71.09, 67.04, 64.75, 44.49, 45.34],
    'Accuracy': [0.80, 1.00, 0.80, 0.40, 0.80, 0.80, 0.80, 0.90]
}

ai_gemini25_data = {
    'Group': ['AI_Gemini_2.5'] * 4,
    'Time_Per_Task': [50.0, 60.0, 92.91, 73.46],
    'Accuracy': [0.40, 0.40, 0.50, 0.10]
}

ai_robo_data = {
    'Group': ['AI_Robotics'] * 2,
    'Time_Per_Task': [58.25, 33.48 ],
    'Accuracy': [0.40, 0.50]
}

df = pd.concat([
    pd.DataFrame(human_data),
    pd.DataFrame(ai_gemini3_data),
    pd.DataFrame(ai_gemini25_data),
    pd.DataFrame(ai_robo_data)
], ignore_index=True)

#CALCULATIONS
df['Error_Rate'] = 1.0 - df['Accuracy']
# Net Efficiency Formula: (Accuracy - Errors) / Time
df['Net_Efficiency'] = (df['Accuracy'] - df['Error_Rate']) / df['Time_Per_Task']

#PLOTTING
plt.figure(figsize=(12, 7))
sns.boxplot(
    x='Group',
    y='Net_Efficiency',
    data=df,
    hue='Group',
    legend=False,
    palette="Set2",
    boxprops=dict(alpha=0.4),
    showfliers=False
)

sns.stripplot(
    x='Group',
    y='Net_Efficiency',
    data=df,
    color='#2c3e50',
    alpha=0.8,
    jitter=0.2,
    size=8,
    edgecolor='white',
    linewidth=1,
    label='Individual Participants'
)

# The Red Zone
plt.axhline(0, color='red', linestyle='--', linewidth=2, label='Random Guessing Baseline')
plt.title('Cognitive Efficiency: Humans vs AI',
          fontsize=14, fontweight='bold', pad=20)
plt.ylabel('Net Efficiency Score\n(Net Correct Answers per Second)', fontsize=12)
plt.xlabel('Group', fontsize=12)
plt.xticks(rotation=10)
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend([handles[-1], handles[-2]], [labels[-1], labels[-2]], loc='upper right')

plt.grid(axis='y', alpha=0.2)
plt.tight_layout()

plt.savefig('cognitive_efficiency.png', dpi=300)
plt.show()

#IDENTIFYING "BAD" PERFORMERS IN TEXT
print("\n=== SESSIONS BELOW RANDOM GUESSING LEVEL (Net Efficiency < 0) ===")
poor_performers = df[df['Net_Efficiency'] < 0].sort_values('Net_Efficiency')
if not poor_performers.empty:
    print(poor_performers[['Group', 'Net_Efficiency', 'Accuracy']])
else:
    print("Not found!")
