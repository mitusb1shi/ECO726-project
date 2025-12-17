import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
import os


# FIGURE 3 - EVENT STUDY - EFFECT OF MEASLES VACCINE ON MEASLES INCIDENCE

# Change directory
os.chdir("/Users/ishi/Desktop/measles project")

# Load data
df = pd.read_stata('inc_rate_ES.dta')

# Periods 1-5
for i in range(1, 6):
    df[f'exp_Mpre_{i}'] = df[f'_Texp_{i}'] * df['avg_12yr_measles_rate']

# Periods 7-18 (skip 6 as it's the omitted reference period)
for i in range(7, 19):
    df[f'exp_Mpre_{i}'] = df[f'_Texp_{i}'] * df['avg_12yr_measles_rate']
    
    
# Prepare variables for regression 
# reg Measles exp_M* _Is* population _T* avg_12yr_measles_rate, cluster(statefip) robust

# exp_M* : all interaction terms we just created (with underscores)
exp_M_cols = [f'exp_Mpre_{i}' for i in range(1, 6)] + [f'exp_Mpre_{i}' for i in range(7, 19)]


# _Is* : state fixed effects - NOTE: In this dataset they're called _Istatefip_*
state_cols = [col for col in df.columns if col.startswith('_Istatefip_')]


# _T* : time variables
# In Stata, _T* matches _Texp_* variables!
# The wildcard _T* includes _Texp_1, _Texp_2, etc.
time_cols = [col for col in df.columns if col.startswith('_Texp_')]

# exp_M* _Is* population _T* avg_12yr_measles_rate
# this becomes: exp_M* _Istatefip_* population avg_12yr_measles_rate
X_cols = exp_M_cols + state_cols + ['population'] + time_cols + ['avg_12yr_measles_rate']


# Prepare regression data - drop rows with any missing values in our variables
reg_data = df[["Measles"] + X_cols + ['statefip']].dropna()

# Set up regression
y = reg_data["Measles"]
X = reg_data[X_cols]

# DO NOT add constant - we have state fixed effects which act as constant


# Remove columns with zero variance
X_std = X.std()
zero_var_cols = X_std[X_std < 1e-10].index.tolist()
if zero_var_cols:
    X = X.drop(columns=zero_var_cols)
    

# Run OLS with clustered standard errors
model = OLS(y, X, missing='drop')
results = model.fit(cov_type='cluster', cov_kwds={'groups': reg_data['statefip']})


# Count state and time fixed effects
state_coefs = [v for v in results.params.index if v.startswith('_Is')]
time_coefs = [v for v in results.params.index if v.startswith('_T') and not v.startswith('_Texp')]

# Extract all results
results_df = pd.DataFrame({
    'var': results.params.index,
    'coef': results.params.values,
    'stderr': results.bse.values,
    'pval': results.pvalues.values,
    'ci_lower': results.conf_int()[0].values,
    'ci_upper': results.conf_int()[1].values,
    'N': int(results.nobs)
})

# Keep only exp_Mpre* coefficients
results_df = results_df[results_df['var'].str.startswith('exp_Mpre')].copy().reset_index(drop=True)


# Add the omitted year (period 6, event time -1)
omitted = pd.DataFrame({
    'var': ['exp_Mpre_6'],
    'coef': [0.0],
    'stderr': [0.0],
    'pval': [np.nan],
    'ci_lower': [0.0],
    'ci_upper': [0.0],
    'N': [int(results.nobs)]
})
results_df = pd.concat([results_df, omitted], ignore_index=True)

event_time_map = {
    'exp_Mpre_1': -6,
    'exp_Mpre_2': -5,
    'exp_Mpre_3': -4,
    'exp_Mpre_4': -3,
    'exp_Mpre_5': -2,
    'exp_Mpre_6': -1,  # Omitted reference period
    'exp_Mpre_7': 0,
    'exp_Mpre_8': 1,
    'exp_Mpre_9': 2,
    'exp_Mpre_10': 3,
    'exp_Mpre_11': 4,
    'exp_Mpre_12': 5,
    'exp_Mpre_13': 6,
    'exp_Mpre_14': 7,
    'exp_Mpre_15': 8,
    'exp_Mpre_16': 9,
    'exp_Mpre_17': 10,
    'exp_Mpre_18': 11
}

results_df['exp'] = results_df['var'].map(event_time_map)

# Sort by event time
results_df = results_df.sort_values('exp').reset_index(drop=True)


# Filter for plotting: exp > -6 & exp < 11
plot_data = results_df[(results_df['exp'] > -6) & (results_df['exp'] < 11)].copy()

print(f"\nPlotting {len(plot_data)} points")

# Create event study graph matching Stata output
fig, ax = plt.subplots(figsize=(10, 6))

# Plot coefficient line (solid gray, thick)
ax.plot(plot_data['exp'], plot_data['coef'], 
        color='gray', linestyle='-', linewidth=2.5, marker='', zorder=3)

# Plot confidence interval lines (dashed gray, medium thick)
ax.plot(plot_data['exp'], plot_data['ci_lower'], 
        color='gray', linestyle='--', linewidth=1.5, marker='', zorder=2)
ax.plot(plot_data['exp'], plot_data['ci_upper'], 
        color='gray', linestyle='--', linewidth=1.5, marker='', zorder=2)


ax.axhline(y=0, color='black', linewidth=1, zorder=1)
ax.axvline(x=-1, color='black', linewidth=1, zorder=1)

ax.set_title('Measles rate by year (per 100,000)', fontsize=10, loc='left', pad=10)
ax.set_xlabel('Years relative to measles vaccine availability', fontsize=10)
ax.set_ylabel('Measles rate by year (per 100,000)', fontsize=10)
ax.set_xlim(-5, 10)
ax.set_ylim(-1.5, 1)
ax.set_xticks([-5, 0, 5, 10])
ax.set_yticks([-1.5, -1, -0.5, 0, 0.5, 1])
ax.tick_params(axis='both', which='major', labelsize=9)
ax.grid(False)
ax.set_facecolor('white')
fig.patch.set_facecolor('white')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('Figure3.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\nFigure saved as Figure3.png")
plt.show()

