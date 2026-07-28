import matplotlib.pyplot as plt
import csv

# Read data
legacy = []
supabase = []

with open('final_dataset.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        val = float(row['API_Response_Time_ms'])
        if row['Architecture_Code'] == '1':
            legacy.append(val)
        else:
            supabase.append(val)

# Calculate means
mean_legacy = sum(legacy) / len(legacy)
mean_supabase = sum(supabase) / len(supabase)

# Calculate standard error for error bars
def std_err(data, mean):
    variance = sum([((x - mean) ** 2) for x in data]) / (len(data) - 1)
    return (variance ** 0.5) / (len(data) ** 0.5)

err_legacy = std_err(legacy, mean_legacy)
err_supabase = std_err(supabase, mean_supabase)

# Plot
labels = ['Legacy SQLite\n(Sequential)', 'Supabase PostgreSQL\n(Multi-threaded)']
means = [mean_legacy, mean_supabase]
errors = [err_legacy, err_supabase]

fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.bar(labels, means, yerr=errors, capsize=10, color=['#4B8BBE', '#306998'], alpha=0.9, edgecolor='black')

ax.set_ylabel('Mean Latency (ms)', fontsize=12, fontweight='bold')
ax.set_title('API Response Latency: Legacy vs Optimized Architecture', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(means) + 20)
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Add value labels on top of bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.1f} ms', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('latency_chart.png', dpi=300)
print("Chart saved as latency_chart.png")
