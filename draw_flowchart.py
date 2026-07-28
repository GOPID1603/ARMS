import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(14, 4))
ax.set_xlim(-1, 15)
ax.set_ylim(-1, 2)
ax.axis('off')

def draw_box(ax, x, y, width, height, text, facecolor):
    box = patches.FancyBboxPatch((x, y), width, height,
                                 boxstyle="round,pad=0.1",
                                 edgecolor="black", facecolor=facecolor, lw=1.5)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center',
            fontsize=10, fontweight='bold', family='sans-serif')

def draw_arrow(ax, x1, y1, x2, y2):
    ax.annotate("",
                xy=(x2, y2), xycoords='data',
                xytext=(x1, y1), textcoords='data',
                arrowprops=dict(arrowstyle="->", color="black", lw=2))

# Colors
orange = '#ffb347'
peach = '#ffdab9'
pink = '#ffb6c1'
green = '#d9ead3'
light_orange = '#fce5cd'
beige = '#fff2cc'

# Draw Boxes
draw_box(ax, 0, 0.3, 1.8, 0.6, "DATA\nCOLLECTION", orange)
draw_box(ax, 2.5, 0.3, 1.8, 0.6, "DATA\nPREPARATION", peach)
draw_box(ax, 5, 0.3, 1.8, 0.6, "ARCHITECTURE\nIMPLEMENTATION", pink)
draw_box(ax, 7.8, 0.8, 1.8, 0.6, "LEGACY SQLITE\nARCHITECTURE", green)
draw_box(ax, 7.8, -0.2, 1.8, 0.6, "SUPABASE\nMULTI-THREADED\nARCHITECTURE", light_orange)
draw_box(ax, 10.6, 0.3, 1.8, 0.6, "PERFORMANCE\nEVALUATION", pink)
draw_box(ax, 13.1, 0.3, 1.8, 0.6, "RESULT\n(IBM SPSS)", beige)

# Draw Arrows
draw_arrow(ax, 1.8, 0.6, 2.5, 0.6) # A -> B
draw_arrow(ax, 4.3, 0.6, 5, 0.6)   # B -> C

# C -> D
ax.plot([6.8, 7.3, 7.3, 7.8], [0.6, 0.6, 1.1, 1.1], color="black", lw=2)
ax.plot(7.8, 1.1, marker='>', color='black', ms=6)

# C -> E
ax.plot([6.8, 7.3, 7.3, 7.8], [0.6, 0.6, 0.1, 0.1], color="black", lw=2)
ax.plot(7.8, 0.1, marker='>', color='black', ms=6)

# D -> F
ax.plot([9.6, 10.1, 10.1, 10.6], [1.1, 1.1, 0.6, 0.6], color="black", lw=2)
ax.plot(10.6, 0.6, marker='>', color='black', ms=6)

# E -> F
ax.plot([9.6, 10.1, 10.1, 10.6], [0.1, 0.1, 0.6, 0.6], color="black", lw=2)
ax.plot(10.6, 0.6, marker='>', color='black', ms=6)

# F -> G
draw_arrow(ax, 12.4, 0.6, 13.1, 0.6)

plt.tight_layout()
plt.savefig('flowchart_formal.png', dpi=300, bbox_inches='tight', facecolor='#e6f2ff')
