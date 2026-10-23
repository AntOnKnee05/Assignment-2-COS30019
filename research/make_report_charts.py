import json, statistics as st, math
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
P=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "")
OUT=os.path.join(P, "results", "figures", ""); os.makedirs(OUT, exist_ok=True)
COL={"DFS":"#2a78d6","BFS":"#eb6834","GBFS":"#1baf7a","AS":"#eda100","CUS1":"#e87ba4","CUS2":"#008300"}
MK={"DFS":"o","BFS":"s","GBFS":"^","AS":"D","CUS1":"v","CUS2":"P"}
M=list(COL)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.spines.top":False,"axes.spines.right":False,
 "axes.edgecolor":"#888","axes.grid":True,"grid.color":"#e6e6e6","grid.linewidth":0.6,"axes.axisbelow":True})

# Fig 1 spec graph
nodes={1:(4,1),2:(2,2),3:(4,4),4:(6,3),5:(5,6),6:(7,5)}
edges=[(2,1,4),(3,1,5),(1,3,5),(2,3,4),(3,2,5),(4,1,6),(1,4,6),(4,3,5),(3,5,6),(5,3,6),(4,5,7),(5,4,8),(6,3,7),(3,6,7)]
fig,ax=plt.subplots(figsize=(4.6,3.6))
es={(a,b) for a,b,_ in edges}
for a,b,c in edges:
    two=(b,a) in es
    if two and a>b: continue
    (x1,y1),(x2,y2)=nodes[a],nodes[b]
    ax.annotate("",xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle="<|-|>" if two else "-|>",color="#5b6670",lw=1.2,shrinkA=11,shrinkB=11,mutation_scale=10))
    lbl=f"{c}" if not two else (f"{c}" if dict(((p,q),w) for p,q,w in edges)[(b,a)]==c else f"{c}/{dict(((p,q),w) for p,q,w in edges)[(b,a)]}")
    t=0.3 if (a,b)==(4,5) else 0.5
    ax.text(x1+(x2-x1)*t,y1+(y2-y1)*t,lbl,fontsize=7.5,color="#333",ha="center",va="center",bbox=dict(boxstyle="round,pad=0.15",fc="white",ec="none"))
for n,(x,y) in nodes.items():
    fc="#cfe8d6" if n==2 else ("#f9d3d3" if n in (4,5) else "white")
    ec="#2f9e44" if n==2 else ("#c92a2a" if n in (4,5) else "#333")
    ax.scatter([x],[y],s=330,c=fc,edgecolors=ec,linewidths=1.6,zorder=3)
    ax.text(x,y,str(n),ha="center",va="center",fontsize=9,fontweight="bold",zorder=4)
ax.set_xlim(1,8);ax.set_ylim(0,7);ax.set_aspect("equal");ax.set_xlabel("x");ax.set_ylabel("y")
ax.text(1.2,6.5,"green = origin (2)\nred = destinations (4, 5)\na/b = cost forward/back",fontsize=7,va="top",color="#444")
fig.tight_layout();fig.savefig(OUT+"fig1_graph.png",dpi=220);plt.close()

# Fig 2 nodes created on grid + other cases (from benchmark.json)
b=json.load(open(P+"results/benchmark.json"))["results"]
cases=["test01_spec_example.txt","test06_cheap_long_vs_short_expensive.txt","test10_greedy_trap.txt","test12_dead_ends.txt","test13_large_grid.txt"]
short=["T1 spec","T6 cheap-long","T10 greedy trap","T12 dead ends","T13 5×5 grid"]
fig,ax=plt.subplots(figsize=(6.6,2.9))
w=0.13
for i,m in enumerate(M):
    vals=[next(r["nodes_created"] for r in b if r["case"]==c and r["method"]==m) for c in cases]
    ax.bar([k+(i-2.5)*w for k in range(len(cases))],vals,w*0.9,color=COL[m],label=m)
ax.set_yscale("log");ax.set_xticks(range(len(cases)));ax.set_xticklabels(short);ax.set_ylabel("Nodes created (log scale)")
ax.grid(axis="x",visible=False);ax.legend(ncol=6,fontsize=7.5,frameon=False,loc="upper left",bbox_to_anchor=(0,1.15))
fig.tight_layout();fig.savefig(OUT+"fig2_nodes_cases.png",dpi=220);plt.close()

# Fig 3 scalability
r=json.load(open(P+"results/research.json"))
g=defaultdict(list)
for x in r["scalability"]: g[(x["n"],x["method"])].append(x)
sizes=sorted({x["n"] for x in r["scalability"]})
fig,axs=plt.subplots(1,2,figsize=(6.8,2.9))
for m in M:
    axs[0].plot(sizes,[st.median(x["nodes"] for x in g[(n,m)]) for n in sizes],color=COL[m],marker=MK[m],ms=5,lw=2,label=m)
    axs[1].plot(sizes,[max(x["nodes"] for x in g[(n,m)]) for n in sizes],color=COL[m],marker=MK[m],ms=5,lw=2,label=m)
for a,t in zip(axs,["Median nodes created","Worst-case nodes created"]):
    a.set_yscale("log");a.set_xlabel("Graph size (nodes)");a.set_title(t,fontsize=9)
axs[0].legend(fontsize=7,frameon=False,ncol=2)
fig.tight_layout();fig.savefig(OUT+"fig3_scaling.png",dpi=220);plt.close()

# Fig 4 path quality
fig,axs=plt.subplots(1,2,figsize=(6.8,2.6))
allr=r["scalability"]
opt=[100*st.mean(x["cost_ratio"]<1+1e-9 for x in allr if x["method"]==m) for m in M]
mov=[100*st.mean(x["moves_ratio"]<1+1e-9 for x in allr if x["method"]==m) for m in M]
for a,v,t in ((axs[0],opt,"% of runs with lowest-cost path"),(axs[1],mov,"% of runs with fewest-moves path")):
    a.bar(M,v,0.6,color=[COL[m] for m in M]);a.set_ylim(0,110);a.set_title(t,fontsize=9);a.grid(axis="x",visible=False)
    for i,val in enumerate(v): a.text(i,val+2,f"{val:.0f}",ha="center",fontsize=7.5,color="#333")
fig.tight_layout();fig.savefig(OUT+"fig4_quality.png",dpi=220);plt.close()

# Fig 5 visit-all
g=defaultdict(list)
for x in r["visit_all"]: g[x["k"]].append(x)
ks=sorted(g)
fig,ax=plt.subplots(figsize=(4.6,2.7))
ax.plot(ks,[st.median(x["state_nodes"] for x in g[k]) for k in ks],marker="o",color="#2a78d6",lw=2,label="State-space A*")
ax.plot(ks,[st.median(x["legs_nodes"] for x in g[k]) for k in ks],marker="s",color="#eb6834",lw=2,label="Pairwise A* legs + Held-Karp")
ax.set_xlabel("Number of destinations (k)");ax.set_ylabel("Median nodes created");ax.set_xticks(ks);ax.legend(frameon=False,fontsize=7.5)
fig.tight_layout();fig.savefig(OUT+"fig5_visitall.png",dpi=220);plt.close()
print("ok")
