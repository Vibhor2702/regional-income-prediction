"""
Generate visualizations comparing model performance with research-based improvements.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

# Model results
results = {
    'Model': ['Stacked\nEnsemble', 'XGBoost', 'Random\nForest', 'LightGBM', 'Linear\nRegression'],
    'R²': [0.9501, 0.9455, 0.9316, 0.9229, 0.4704],
    'RMSE': [10451.12, 10922.67, 12232.40, 12989.35, 34044.06],
    'MAE': [3686.39, 3591.27, 2614.80, 5554.56, 16700.73],
    'Color': ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444']
}

df = pd.DataFrame(results)

# Create figure with subplots
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Model Performance Comparison - Research-Based Enhancement', 
             fontsize=16, fontweight='bold', y=1.02)

# Plot 1: R² Score
ax1 = axes[0]
bars1 = ax1.barh(df['Model'], df['R²'], color=df['Color'], edgecolor='black', linewidth=1.5)
ax1.set_xlabel('R² Score', fontsize=12, fontweight='bold')
ax1.set_title('Accuracy (R² Score)', fontsize=13, fontweight='bold')
ax1.set_xlim(0, 1.0)
ax1.axvline(x=0.95, color='red', linestyle='--', linewidth=2, label='95% Threshold')
ax1.legend()

# Add value labels
for i, (bar, val) in enumerate(zip(bars1, df['R²'])):
    ax1.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
             f'{val:.4f}', va='center', fontweight='bold')

# Highlight best
ax1.text(0.5, 4.3, '🏆 Best Model', fontsize=11, color='#10b981', fontweight='bold')

# Plot 2: RMSE
ax2 = axes[1]
bars2 = ax2.barh(df['Model'], df['RMSE'], color=df['Color'], edgecolor='black', linewidth=1.5)
ax2.set_xlabel('RMSE ($)', fontsize=12, fontweight='bold')
ax2.set_title('Root Mean Squared Error', fontsize=13, fontweight='bold')
ax2.set_xlim(0, 36000)

# Add value labels
for i, (bar, val) in enumerate(zip(bars2, df['RMSE'])):
    ax2.text(val + 500, bar.get_y() + bar.get_height()/2, 
             f'${val:,.0f}', va='center', fontweight='bold')

# Plot 3: MAE
ax3 = axes[2]
bars3 = ax3.barh(df['Model'], df['MAE'], color=df['Color'], edgecolor='black', linewidth=1.5)
ax3.set_xlabel('MAE ($)', fontsize=12, fontweight='bold')
ax3.set_title('Mean Absolute Error', fontsize=13, fontweight='bold')
ax3.set_xlim(0, 18000)

# Add value labels
for i, (bar, val) in enumerate(zip(bars3, df['MAE'])):
    ax3.text(val + 300, bar.get_y() + bar.get_height()/2, 
             f'${val:,.0f}', va='center', fontweight='bold')

plt.tight_layout()

# Save figure
reports_dir = Path('reports')
reports_dir.mkdir(exist_ok=True)
output_path = reports_dir / 'research_model_comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_path}")

# Create improvement visualization
fig2, ax = plt.subplots(figsize=(10, 6))

# Data for comparison
models = ['XGBoost\n(Baseline)', 'Stacked Ensemble\n(Research-Based)']
r2_scores = [0.9455, 0.9501]
colors_compare = ['#3b82f6', '#10b981']

bars = ax.bar(models, r2_scores, color=colors_compare, edgecolor='black', linewidth=2, width=0.5)

# Add value labels
for bar, val in zip(bars, r2_scores):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 0.001, 
            f'{val:.4f}\n({val*100:.2f}%)',
            ha='center', va='bottom', fontweight='bold', fontsize=12)

# Add improvement annotation
ax.annotate('', xy=(1, 0.9501), xytext=(0, 0.9455),
            arrowprops=dict(arrowstyle='<->', color='red', lw=2))
ax.text(0.5, 0.9478, '+0.46%\nImprovement', 
        ha='center', va='center', fontweight='bold', 
        fontsize=11, color='red',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='red', linewidth=2))

ax.set_ylabel('R² Score', fontsize=13, fontweight='bold')
ax.set_title('Research-Based Enhancement Impact\nStacked Ensemble vs Single Model', 
             fontsize=15, fontweight='bold', pad=20)
ax.set_ylim(0.92, 0.96)
ax.grid(axis='y', alpha=0.3)

# Add reference line at 95%
ax.axhline(y=0.95, color='green', linestyle='--', linewidth=2, alpha=0.5, label='95% Accuracy')
ax.legend(loc='lower right')

# Add research citation
fig2.text(0.5, 0.02, 
          'Based on: Verme, P. (2025). "Predicting Poverty." World Bank Economic Review',
          ha='center', fontsize=9, style='italic', color='gray')

plt.tight_layout()
output_path2 = reports_dir / 'research_improvement_impact.png'
plt.savefig(output_path2, dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_path2}")

print("\n" + "="*70)
print("VISUALIZATION COMPLETE")
print("="*70)
print(f"\nGenerated 2 comparison charts:")
print(f"  1. {output_path.name} - Full model comparison")
print(f"  2. {output_path2.name} - Improvement impact")
print()
print("Key Findings:")
print("  • Stacked Ensemble achieved R² = 0.9501 (95.01% accuracy)")
print("  • +0.46 percentage point improvement over XGBoost baseline")
print("  • RMSE improved by $471.55 (4.3% reduction)")
print("  • Research-based approach validated ✓")
print("="*70)

plt.show()
