"""
EcoMonitor Dashboard - Completo
Schermate: Overview, Data Table, Locations, Students, Settings
Dipendenze: pip install customtkinter matplotlib
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import csv, os
from collections import defaultdict

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ─── TEMA DINAMICO ────────────────────────────────────────────────
THEME = {"dark": False}

def T(light_val, dark_val):
    return dark_val if THEME["dark"] else light_val

def BG():        return T("#F5F5F0", "#1A1A1A")
def SIDEBAR():   return T("#FFFFFF", "#111111")
def CARD():      return T("#FFFFFF", "#2A2A2A")
def CARD_DARK(): return T("#1C1C1E", "#0D0D0D")
def TEXT():      return T("#1A1A1A", "#F0F0F0")
def SUBTEXT():   return T("#888888", "#999999")
def BORDER():    return T("#E8E8E8", "#333333")
def GRID_C():    return T("#E8E8E8", "#333333")
def PLOT_BG():   return T("#FFFFFF", "#2A2A2A")
def PLOT_DARK(): return T("#1C1C1E", "#0D0D0D")

C_ACCENT    = "#F5A623"
C_ACCENT_BG = "#FEF3E2"
C_BAR_LUX   = "#FBBF7C"
C_BAR_DB    = "#5B9BD5"
C_LINE_LUX  = "#D4956A"
C_LINE_DB   = "#5B9BD5"
C_DONUT     = ["#F5A623","#E8845A","#C0392B","#8B1A1A","#D4633A","#F0C080","#FDDCB0","#E06030"]

ROOMS = {"Room A":"#F5A623","Room B":"#5B9BD5","Room C":"#4CAF50","Room D":"#E05C5C"}
CSV_FILE = "dati_phyphox.csv"

APP_REF = None  # riferimento globale all'app per il cambio tema

def leggi_dati():
    if not os.path.exists(CSV_FILE): return []
    with open(CSV_FILE, newline="") as f: return list(csv.DictReader(f))

# ─── WIDGET BASE ──────────────────────────────────────────────────
class Card(ctk.CTkFrame):
    def __init__(self, master, dark=False, **kw):
        super().__init__(master,
            fg_color=CARD_DARK() if dark else CARD(),
            corner_radius=12,
            border_width=0 if dark else 1,
            border_color=BORDER(), **kw)

def plot_bar(frame, labels, values, color, dark=False):
    bg = PLOT_DARK() if dark else PLOT_BG()
    tc = "#888888" if dark else SUBTEXT()
    gc = "#333333" if dark else GRID_C()
    for w in frame.winfo_children(): w.destroy()
    fig = Figure(figsize=(5,3), dpi=90, facecolor=bg)
    ax = fig.add_subplot(111, facecolor=bg)
    ax.bar(labels or ["—"], values or [0], color=color, width=0.5, zorder=3)
    ax.set_axisbelow(True); ax.yaxis.grid(True, color=gc, linestyle="--", linewidth=0.8)
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    ax.tick_params(colors=tc, labelsize=9); ax.set_ylim(bottom=0)
    fig.tight_layout(pad=1.2)
    FigureCanvasTkAgg(fig, frame).get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)

def plot_line(frame, ts, vals, color):
    bg = PLOT_DARK()
    for w in frame.winfo_children(): w.destroy()
    fig = Figure(figsize=(5,3), dpi=90, facecolor=bg)
    ax = fig.add_subplot(111, facecolor=bg)
    if vals:
        x = list(range(len(vals)))
        ax.plot(x, vals, color=color, linewidth=2, zorder=3)
        ax.fill_between(x, vals, min(vals), alpha=0.3, color=color)
        step = max(1, len(ts)//6)
        ax.set_xticks(x[::step])
        ax.set_xticklabels([t[-5:] for t in ts[::step]], rotation=0, fontsize=8)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#333333", linestyle="--", linewidth=0.6)
    ax.xaxis.grid(True, color="#333333", linestyle="--", linewidth=0.6)
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    ax.tick_params(colors="#888888", labelsize=8)
    fig.tight_layout(pad=1.2)
    FigureCanvasTkAgg(fig, frame).get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)

def setup_treeview_style(name, dark=False):
    bg = CARD_DARK() if dark else CARD()
    fg = "#FFFFFF" if dark else TEXT()
    hfg = "#888888" if dark else SUBTEXT()
    style = ttk.Style(); style.theme_use("clam")
    style.configure(f"{name}.Treeview", background=bg, foreground=fg,
        fieldbackground=bg, rowheight=40, font=("Helvetica",12), borderwidth=0)
    style.configure(f"{name}.Treeview.Heading", background=bg, foreground=hfg,
        font=("Helvetica",12), borderwidth=0, relief="flat")
    style.map(f"{name}.Treeview", background=[("selected", "#3A3A3A" if dark else "#F0F0F0")])
    style.layout(f"{name}.Treeview", [(f"{name}.Treeview.treearea", {"sticky":"nswe"})])

class StatCard(Card):
    def __init__(self, master, title, value, unit, icon, **kw):
        super().__init__(master, **kw); self.configure(height=100)
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont("Helvetica",13), text_color=SUBTEXT()).place(x=20, y=18)
        vf = ctk.CTkFrame(self, fg_color="transparent"); vf.place(x=20, y=42)
        self.val = ctk.CTkLabel(vf, text=str(value), font=ctk.CTkFont("Helvetica",32,weight="bold"), text_color=TEXT())
        self.val.pack(side="left")
        ctk.CTkLabel(vf, text=f" {unit}", font=ctk.CTkFont("Helvetica",14), text_color=SUBTEXT()).pack(side="left", pady=(10,0))
        ib = ctk.CTkFrame(self, fg_color=C_ACCENT_BG, corner_radius=10, width=48, height=48)
        ib.place(relx=1.0, x=-20, y=26, anchor="ne")
        ctk.CTkLabel(ib, text=icon, font=ctk.CTkFont("Helvetica",20), text_color=C_ACCENT).place(relx=0.5, rely=0.5, anchor="center")
    def aggiorna(self, v): self.val.configure(text=str(v))

# ══════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════
class OverviewFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BG(), **kw); self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Dashboard Overview", font=ctk.CTkFont("Helvetica",28,weight="bold"), text_color=TEXT()).pack(anchor="w", padx=30, pady=(30,2))
        ctk.CTkLabel(self, text="Environmental monitoring metrics and insights", font=ctk.CTkFont("Helvetica",13), text_color=SUBTEXT()).pack(anchor="w", padx=30, pady=(0,20))
        fc = Card(self); fc.pack(fill="x", padx=30, pady=(0,20))
        fi = ctk.CTkFrame(fc, fg_color="transparent"); fi.pack(fill="x", padx=20, pady=15)
        for label, var_name, values in [
            ("Select Sensor","sensor_var",["All Sensors","Luminosity","Noise"]),
            ("Select Location","loc_var",["All Locations","Room A","Room B","Room C","Room D"]),
        ]:
            f = ctk.CTkFrame(fi, fg_color="transparent"); f.pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont("Helvetica",12), text_color=SUBTEXT()).pack(anchor="w")
            var = ctk.StringVar(value=values[0]); setattr(self, var_name, var)
            ctk.CTkComboBox(f, variable=var, values=values, fg_color=CARD(), border_color=BORDER(),
                button_color=BORDER(), button_hover_color=C_ACCENT, dropdown_fg_color=CARD(),
                text_color=TEXT(), width=300, height=40, corner_radius=8,
                command=lambda _: self.aggiorna()).pack(anchor="w", pady=(4,0))
        sf = ctk.CTkFrame(self, fg_color="transparent"); sf.pack(fill="x", padx=30, pady=(0,20))
        sf.columnconfigure((0,1,2), weight=1, uniform="col")
        self.c_total = StatCard(sf,"Total Measurements","0","","🗄",height=100); self.c_total.grid(row=0,column=0,padx=(0,10),sticky="ew")
        self.c_lux   = StatCard(sf,"Average Luminosity","0","lux","💡",height=100); self.c_lux.grid(row=0,column=1,padx=5,sticky="ew")
        self.c_db    = StatCard(sf,"Average Noise","0","dB","🔊",height=100); self.c_db.grid(row=0,column=2,padx=(10,0),sticky="ew")
        gf = ctk.CTkFrame(self, fg_color="transparent"); gf.pack(fill="x", padx=30, pady=(0,20))
        gf.columnconfigure(0, weight=3); gf.columnconfigure(1, weight=2)
        bc = Card(gf); bc.grid(row=0,column=0,padx=(0,10),sticky="nsew")
        ctk.CTkLabel(bc, text="Measurements by Location", font=ctk.CTkFont("Helvetica",15,weight="bold"), text_color=TEXT()).pack(anchor="w", padx=20, pady=(18,0))
        self.bar_f = ctk.CTkFrame(bc, fg_color="transparent"); self.bar_f.pack(fill="both", expand=True, padx=10, pady=(0,10))
        dc = Card(gf); dc.grid(row=0,column=1,padx=(10,0),sticky="nsew")
        ctk.CTkLabel(dc, text="Measurements per Student", font=ctk.CTkFont("Helvetica",15,weight="bold"), text_color=TEXT()).pack(anchor="w", padx=20, pady=(18,0))
        self.donut_f = ctk.CTkFrame(dc, fg_color="transparent"); self.donut_f.pack(fill="both", expand=True, padx=10, pady=(0,10))
        rc = Card(self); rc.pack(fill="x", padx=30, pady=(0,30))
        ctk.CTkLabel(rc, text="Recent Measurements", font=ctk.CTkFont("Helvetica",15,weight="bold"), text_color=TEXT()).pack(anchor="w", padx=20, pady=(18,10))
        setup_treeview_style("Eco")
        cols = ("Student","Sensor","Value","Location","Date/Time")
        self.tree = ttk.Treeview(rc, columns=cols, show="headings", style="Eco.Treeview", height=8)
        for c in cols: self.tree.heading(c,text=c); self.tree.column(c,anchor="w",width=180)
        self.tree.pack(fill="x", padx=20, pady=(0,20))
        self.aggiorna()

    def aggiorna(self):
        rows = leggi_dati()
        sf = self.sensor_var.get()
        if sf=="Luminosity": rows=[r for r in rows if r.get("luce_lux","")]
        elif sf=="Noise":    rows=[r for r in rows if r.get("rumore_db","")]
        lux_v=[float(r["luce_lux"]) for r in rows if r.get("luce_lux") not in ("","None",None)]
        db_v =[float(r["rumore_db"]) for r in rows if r.get("rumore_db") not in ("","None",None)]
        self.c_total.aggiorna(len(rows))
        self.c_lux.aggiorna(round(sum(lux_v)/len(lux_v)) if lux_v else 0)
        self.c_db.aggiorna(round(sum(db_v)/len(db_v)) if db_v else 0)
        per_mac=defaultdict(int)
        for r in rows: per_mac[r.get("mac_address","?")[:8]]+=1
        plot_bar(self.bar_f, list(per_mac.keys()), list(per_mac.values()), C_BAR_LUX)
        self._donut(per_mac)
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in reversed(rows[-50:]):
            mac=r.get("mac_address","?")[:17]; ts=r.get("timestamp_pc","")[:16]
            lux=r.get("luce_lux",""); db=r.get("rumore_db","")
            if lux: self.tree.insert("","end",values=(mac,"Luminosity",f"{round(float(lux))} lux","—",ts))
            if db:  self.tree.insert("","end",values=(mac,"Noise",f"{round(float(db))} dB","—",ts))

    def _donut(self, data):
        for w in self.donut_f.winfo_children(): w.destroy()
        fig = Figure(figsize=(4,3), dpi=96, facecolor=PLOT_BG())
        ax = fig.add_subplot(111, facecolor=PLOT_BG())
        labels=list(data.keys()) or ["No data"]; vals=list(data.values()) or [1]
        total=sum(vals); pcts=[f"{l} {round(v/total*100)}%" for l,v in zip(labels,vals)]
        wedges,_=ax.pie(vals,colors=C_DONUT[:len(labels)],wedgeprops=dict(width=0.5,edgecolor="white",linewidth=2),startangle=90)
        ax.legend(wedges,pcts,loc="center left",bbox_to_anchor=(1,0.5),fontsize=8,frameon=False,labelcolor=C_ACCENT)
        fig.tight_layout(pad=1.0)
        FigureCanvasTkAgg(fig, self.donut_f).get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

# ══════════════════════════════════════════════════════════════════
# DATA TABLE
# ══════════════════════════════════════════════════════════════════
class DataTableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BG(), **kw); self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Data Table", font=ctk.CTkFont("Helvetica",28,weight="bold"), text_color=TEXT()).pack(anchor="w", padx=30, pady=(30,2))
        ctk.CTkLabel(self, text="Complete measurement records", font=ctk.CTkFont("Helvetica",13), text_color=SUBTEXT()).pack(anchor="w", padx=30, pady=(0,20))
        top=ctk.CTkFrame(self,fg_color="transparent"); top.pack(fill="x",padx=30,pady=(0,20))
        top.columnconfigure((0,1),weight=1,uniform="col")
        self._build_stat_dark(top,"Luminosity Statistics",0)
        self._build_stat_dark(top,"Noise Statistics",1)
        gf=ctk.CTkFrame(self,fg_color="transparent"); gf.pack(fill="x",padx=30,pady=(0,20))
        gf.columnconfigure((0,1),weight=1,uniform="col")
        for title,attr,row,col,pad in [
            ("Luminosity Over Time","lux_time_f",0,0,(0,10)),
            ("Average Luminosity by Location","lux_loc_f",0,1,(10,0)),
            ("Noise Levels Over Time","db_time_f",1,0,(0,10)),
            ("Average Noise by Location","db_loc_f",1,1,(10,0)),
        ]:
            c=Card(gf,dark=True); c.grid(row=row,column=col,padx=pad,pady=(0,10),sticky="nsew")
            ctk.CTkLabel(c,text=title,font=ctk.CTkFont("Helvetica",14,weight="bold"),text_color="#FFFFFF").pack(anchor="w",padx=18,pady=(16,0))
            f=ctk.CTkFrame(c,fg_color="transparent"); f.pack(fill="both",expand=True,padx=10,pady=(0,10))
            setattr(self,attr,f)
        tc=Card(self,dark=True); tc.pack(fill="x",padx=30,pady=(0,30))
        hf=ctk.CTkFrame(tc,fg_color="transparent"); hf.pack(fill="x",padx=20,pady=(18,10))
        self.count_lbl=ctk.CTkLabel(hf,text="All Measurements (0)",font=ctk.CTkFont("Helvetica",15,weight="bold"),text_color="#FFFFFF")
        self.count_lbl.pack(side="left")
        sf2=ctk.CTkFrame(hf,fg_color="#2C2C2E",corner_radius=20); sf2.pack(side="right")
        ctk.CTkLabel(sf2,text="🔍",font=ctk.CTkFont("Helvetica",13),text_color="#888888").pack(side="left",padx=(12,4))
        self.search_var=ctk.StringVar(); self.search_var.trace("w",lambda *_: self._filter())
        ctk.CTkEntry(sf2,textvariable=self.search_var,placeholder_text="Search...",
            fg_color="transparent",border_width=0,text_color="#FFFFFF",placeholder_text_color="#888888",
            width=260,height=36).pack(side="left",padx=(0,12))
        setup_treeview_style("Dark", dark=True)
        cols=("#","Student","Sensor","Value","Location","Date/Time")
        self.table=ttk.Treeview(tc,columns=cols,show="headings",style="Dark.Treeview",height=15)
        for c,w in zip(cols,[60,200,120,120,120,180]): self.table.heading(c,text=c); self.table.column(c,anchor="w",width=w)
        self.table.pack(fill="x",padx=20,pady=(0,20))
        self._all_rows=[]
        self.aggiorna()

    def _build_stat_dark(self, parent, title, col):
        card=Card(parent,dark=True); card.grid(row=0,column=col,padx=(0,10) if col==0 else (10,0),sticky="ew")
        inner=ctk.CTkFrame(card,fg_color="transparent"); inner.pack(fill="x",padx=20,pady=18)
        hf=ctk.CTkFrame(inner,fg_color="transparent"); hf.pack(fill="x")
        ib=ctk.CTkFrame(hf,fg_color=C_ACCENT_BG,corner_radius=8,width=36,height=36); ib.pack(side="left"); ib.pack_propagate(False)
        ctk.CTkLabel(ib,text="📈",font=ctk.CTkFont("Helvetica",16),text_color=C_ACCENT).place(relx=0.5,rely=0.5,anchor="center")
        ctk.CTkLabel(hf,text=title,font=ctk.CTkFont("Helvetica",15,weight="bold"),text_color="#FFFFFF").pack(side="left",padx=10)
        vf=ctk.CTkFrame(inner,fg_color="transparent"); vf.pack(fill="x",pady=(12,0))
        vf.columnconfigure((0,1,2),weight=1,uniform="v")
        is_lux="Luminosity" in title; unit="lux" if is_lux else "dB"
        for i,(lbl,attr,color) in enumerate([
            ("Average","lux_avg" if is_lux else "db_avg","#FFFFFF"),
            ("↗ Maximum","lux_max" if is_lux else "db_max","#4ADE80"),
            ("↘ Minimum","lux_min" if is_lux else "db_min","#60A5FA"),
        ]):
            f=ctk.CTkFrame(vf,fg_color="transparent"); f.grid(row=0,column=i,sticky="w")
            ctk.CTkLabel(f,text=lbl,font=ctk.CTkFont("Helvetica",11),text_color="#888888").pack(anchor="w")
            vr=ctk.CTkFrame(f,fg_color="transparent"); vr.pack(anchor="w")
            lv=ctk.CTkLabel(vr,text="0",font=ctk.CTkFont("Helvetica",26,weight="bold"),text_color=color); lv.pack(side="left")
            ctk.CTkLabel(vr,text=f" {unit}",font=ctk.CTkFont("Helvetica",11),text_color="#888888").pack(side="left",pady=(8,0))
            setattr(self,attr,lv)

    def aggiorna(self):
        rows=leggi_dati(); lux_v=[]; db_v=[]; lux_ts=[]; db_ts=[]
        for r in rows:
            if r.get("luce_lux") not in ("","None",None):
                try: lux_v.append(float(r["luce_lux"])); lux_ts.append(r.get("timestamp_pc","")[:16])
                except: pass
            if r.get("rumore_db") not in ("","None",None):
                try: db_v.append(float(r["rumore_db"])); db_ts.append(r.get("timestamp_pc","")[:16])
                except: pass
        if lux_v:
            self.lux_avg.configure(text=str(round(sum(lux_v)/len(lux_v),1)))
            self.lux_max.configure(text=str(round(max(lux_v),1)))
            self.lux_min.configure(text=str(round(min(lux_v),1)))
        if db_v:
            self.db_avg.configure(text=str(round(sum(db_v)/len(db_v),1)))
            self.db_max.configure(text=str(round(max(db_v),1)))
            self.db_min.configure(text=str(round(min(db_v),1)))
        plot_line(self.lux_time_f,lux_ts,lux_v,C_LINE_LUX)
        plot_line(self.db_time_f,db_ts,db_v,C_LINE_DB)
        per_mac_lux=defaultdict(list); per_mac_db=defaultdict(list)
        for r in rows:
            mac=r.get("mac_address","?")[:8]
            if r.get("luce_lux") not in ("","None",None):
                try: per_mac_lux[mac].append(float(r["luce_lux"]))
                except: pass
            if r.get("rumore_db") not in ("","None",None):
                try: per_mac_db[mac].append(float(r["rumore_db"]))
                except: pass
        plot_bar(self.lux_loc_f,[*per_mac_lux],[round(sum(v)/len(v)) for v in per_mac_lux.values()],C_BAR_LUX,dark=True)
        plot_bar(self.db_loc_f, [*per_mac_db], [round(sum(v)/len(v)) for v in per_mac_db.values()], C_BAR_DB, dark=True)
        self._all_rows=[]
        for i,r in enumerate(reversed(rows),1):
            mac=r.get("mac_address","?")[:17]; ts=r.get("timestamp_pc","")[:16]
            lux=r.get("luce_lux",""); db=r.get("rumore_db","")
            if lux: self._all_rows.append((f"#{len(rows)-i+1}",mac,"Luminosity",f"{round(float(lux))} lux","—",ts))
            if db:  self._all_rows.append((f"#{len(rows)-i+1}",mac,"Noise",f"{round(float(db))} dB","—",ts))
        self.count_lbl.configure(text=f"All Measurements ({len(self._all_rows)})")
        self._filter()

    def _filter(self):
        q=self.search_var.get().lower()
        for i in self.table.get_children(): self.table.delete(i)
        for row in self._all_rows:
            if q in " ".join(str(c) for c in row).lower():
                self.table.insert("","end",values=row)

# ══════════════════════════════════════════════════════════════════
# LOCATIONS
# ══════════════════════════════════════════════════════════════════
class LocationsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BG(), **kw); self._build()

    def _build(self):
        ctk.CTkLabel(self,text="Locations",font=ctk.CTkFont("Helvetica",28,weight="bold"),text_color=TEXT()).pack(anchor="w",padx=30,pady=(30,2))
        ctk.CTkLabel(self,text="Manage monitoring locations",font=ctk.CTkFont("Helvetica",13),text_color=SUBTEXT()).pack(anchor="w",padx=30,pady=(0,20))
        mc=Card(self); mc.pack(fill="x",padx=30,pady=(0,20))
        ctk.CTkLabel(mc,text="📍  Measurement Locations Map",font=ctk.CTkFont("Helvetica",15,weight="bold"),text_color=TEXT()).pack(anchor="w",padx=20,pady=(18,10))
        map_bg = "#2A2A2A" if THEME["dark"] else "#F8F8F6"
        self.map_canvas=tk.Canvas(mc,bg=map_bg,height=420,highlightthickness=0)
        self.map_canvas.pack(fill="x",padx=20,pady=(0,4))
        ctk.CTkLabel(mc,text="Circle size represents the number of measurements taken at each location",font=ctk.CTkFont("Helvetica",11),text_color=SUBTEXT()).pack(pady=(0,16))
        rf=ctk.CTkFrame(self,fg_color="transparent"); rf.pack(fill="x",padx=30,pady=(0,20))
        rf.columnconfigure((0,1,2,3),weight=1,uniform="room")
        self._room_labels={}
        for i,(room,color) in enumerate(ROOMS.items()):
            c=Card(rf); c.grid(row=0,column=i,padx=(0 if i==0 else 4,4 if i<3 else 0),sticky="ew")
            hf=ctk.CTkFrame(c,fg_color="transparent"); hf.pack(fill="x",padx=16,pady=(14,0))
            ctk.CTkLabel(hf,text=room,font=ctk.CTkFont("Helvetica",14,weight="bold"),text_color=TEXT()).pack(side="left")
            dot=tk.Canvas(hf,width=12,height=12,bg=CARD(),highlightthickness=0); dot.create_oval(1,1,11,11,fill=color,outline=""); dot.pack(side="right",pady=2)
            lbls={}
            for txt,key,col2 in [("↗ Total","total",TEXT()),("💡 Luminosity","lux",C_ACCENT),("🔊 Noise","db",C_BAR_DB)]:
                rf2=ctk.CTkFrame(c,fg_color="transparent"); rf2.pack(fill="x",padx=16,pady=2)
                ctk.CTkLabel(rf2,text=txt,font=ctk.CTkFont("Helvetica",11),text_color=SUBTEXT()).pack(side="left")
                lv=ctk.CTkLabel(rf2,text="0",font=ctk.CTkFont("Helvetica",11,weight="bold"),text_color=col2); lv.pack(side="right"); lbls[key]=lv
            ctk.CTkFrame(c,fg_color=BORDER(),height=1).pack(fill="x",padx=16,pady=6)
            for txt,key,col2 in [("Avg Lum","avg_lux",C_ACCENT),("Avg Noise","avg_db",C_BAR_DB)]:
                rf3=ctk.CTkFrame(c,fg_color="transparent"); rf3.pack(fill="x",padx=16,pady=1)
                ctk.CTkLabel(rf3,text=txt,font=ctk.CTkFont("Helvetica",11),text_color=SUBTEXT()).pack(side="left")
                lv=ctk.CTkLabel(rf3,text="—",font=ctk.CTkFont("Helvetica",12,weight="bold"),text_color=col2); lv.pack(side="right",pady=(0,2)); lbls[key]=lv
            ctk.CTkFrame(c,fg_color="transparent",height=8).pack()
            self._room_labels[room]=lbls
        gf=ctk.CTkFrame(self,fg_color="transparent"); gf.pack(fill="x",padx=30,pady=(0,20))
        gf.columnconfigure((0,1),weight=1,uniform="gc")
        bc=Card(gf); bc.grid(row=0,column=0,padx=(0,10),sticky="nsew")
        ctk.CTkLabel(bc,text="Total Measurements by Location",font=ctk.CTkFont("Helvetica",14,weight="bold"),text_color=TEXT()).pack(anchor="w",padx=18,pady=(16,0))
        self.bar_f=ctk.CTkFrame(bc,fg_color="transparent"); self.bar_f.pack(fill="both",expand=True,padx=10,pady=(0,10))
        sc=Card(gf); sc.grid(row=0,column=1,padx=(10,0),sticky="nsew")
        ctk.CTkLabel(sc,text="Sensor Type Distribution",font=ctk.CTkFont("Helvetica",14,weight="bold"),text_color=TEXT()).pack(anchor="w",padx=18,pady=(16,0))
        self.sensor_f=ctk.CTkFrame(sc,fg_color="transparent"); self.sensor_f.pack(fill="both",expand=True,padx=10,pady=(0,10))
        dc=Card(self); dc.pack(fill="x",padx=30,pady=(0,30))
        ctk.CTkLabel(dc,text="Location Details",font=ctk.CTkFont("Helvetica",15,weight="bold"),text_color=TEXT()).pack(anchor="w",padx=20,pady=(18,10))
        setup_treeview_style("Loc")
        cols=("Location","Total Measurements","Luminosity Count","Noise Count","Avg Luminosity","Avg Noise")
        self.loc_tbl=ttk.Treeview(dc,columns=cols,show="headings",style="Loc.Treeview",height=4)
        for c,w in zip(cols,[150,180,160,140,160,140]): self.loc_tbl.heading(c,text=c); self.loc_tbl.column(c,anchor="w",width=w)
        self.loc_tbl.pack(fill="x",padx=20,pady=(0,20))
        self.aggiorna()

    def _room_data(self, rows):
        data={r:{"lux":[],"db":[],"total":0} for r in ROOMS}
        rl=list(ROOMS.keys())
        for i,row in enumerate(rows):
            room=rl[i%4]; data[room]["total"]+=1
            if row.get("luce_lux") not in ("","None",None):
                try: data[room]["lux"].append(float(row["luce_lux"]))
                except: pass
            if row.get("rumore_db") not in ("","None",None):
                try: data[room]["db"].append(float(row["rumore_db"]))
                except: pass
        return data

    def aggiorna(self):
        rows=leggi_dati(); rd=self._room_data(rows)
        for room,lbls in self._room_labels.items():
            d=rd[room]
            lbls["total"].configure(text=str(d["total"]))
            lbls["lux"].configure(text=str(len(d["lux"])))
            lbls["db"].configure(text=str(len(d["db"])))
            lbls["avg_lux"].configure(text=f"{round(sum(d['lux'])/len(d['lux']))} lux" if d["lux"] else "—")
            lbls["avg_db"].configure(text=f"{round(sum(d['db'])/len(d['db']))} dB" if d["db"] else "—")
        self._disegna_mappa(rd)
        plot_bar(self.bar_f,list(ROOMS.keys()),[rd[r]["total"] for r in ROOMS],C_BAR_LUX)
        self._sensor_dist(rd)
        for i in self.loc_tbl.get_children(): self.loc_tbl.delete(i)
        for room,d in rd.items():
            al=f"{round(sum(d['lux'])/len(d['lux']),1)} lux" if d["lux"] else "—"
            ad=f"{round(sum(d['db'])/len(d['db']),1)} dB" if d["db"] else "—"
            self.loc_tbl.insert("","end",values=(room,d["total"],len(d["lux"]),len(d["db"]),al,ad))

    def _disegna_mappa(self, rd):
        self.map_canvas.delete("all")
        w=self.map_canvas.winfo_width() or 860
        positions={"Room A":(0,0),"Room B":(1,0),"Room C":(0,1),"Room D":(1,1)}
        cw,ch=w//2,195
        box_fill = "#2E2E2E" if THEME["dark"] else "#FAFAFA"
        txt_color = "#CCCCCC" if THEME["dark"] else "#1A1A1A"
        for room,(cx,cy) in positions.items():
            x0=cx*cw+40; y0=cy*ch+10; x1=(cx+1)*cw-40; y1=(cy+1)*ch-10
            self.map_canvas.create_rectangle(x0,y0,x1,y1,outline=BORDER(),fill=box_fill,width=1)
            mx=(x0+x1)//2; my=(y0+y1)//2
            self.map_canvas.create_text(mx,y0+22,text=room,font=("Helvetica",13),fill=txt_color)
            total=rd[room]["total"]; r2=max(22,min(42,20+total*5))
            self.map_canvas.create_oval(mx-r2,my-r2+10,mx+r2,my+r2+10,fill=ROOMS[room],outline="white",width=2)
            self.map_canvas.create_text(mx,my+10,text=str(total),font=("Helvetica",14,"bold"),fill="white")

    def _sensor_dist(self, rd):
        for w in self.sensor_f.winfo_children(): w.destroy()
        fig=Figure(figsize=(5,3),dpi=90,facecolor=PLOT_BG())
        ax=fig.add_subplot(111,facecolor=PLOT_BG())
        rooms=list(ROOMS.keys()); x=range(len(rooms)); w2=0.35
        ax.bar([i-w2/2 for i in x],[len(rd[r]["lux"]) for r in rooms],w2,color=C_BAR_LUX,label="Luminosity",zorder=3)
        ax.bar([i+w2/2 for i in x],[len(rd[r]["db"])  for r in rooms],w2,color=C_BAR_DB, label="Noise",     zorder=3)
        ax.set_xticks(list(x)); ax.set_xticklabels(rooms)
        ax.set_axisbelow(True); ax.yaxis.grid(True,color=GRID_C(),linestyle="--",linewidth=0.8)
        ax.spines[["top","right","left","bottom"]].set_visible(False)
        ax.tick_params(colors=SUBTEXT(),labelsize=9); ax.set_ylim(bottom=0)
        ax.legend(frameon=False,fontsize=9)
        fig.tight_layout(pad=1.2)
        FigureCanvasTkAgg(fig,self.sensor_f).get_tk_widget().pack(fill="both",expand=True)
        plt.close(fig)

# ══════════════════════════════════════════════════════════════════
# STUDENTS
# ══════════════════════════════════════════════════════════════════
class StudentsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BG(), **kw); self._build()

    def _build(self):
        ctk.CTkLabel(self,text="Students",font=ctk.CTkFont("Helvetica",28,weight="bold"),text_color=TEXT()).pack(anchor="w",padx=30,pady=(30,2))
        ctk.CTkLabel(self,text="Student participation and performance",font=ctk.CTkFont("Helvetica",13),text_color=SUBTEXT()).pack(anchor="w",padx=30,pady=(0,20))
        self.grid_f=ctk.CTkFrame(self,fg_color="transparent"); self.grid_f.pack(fill="x",padx=30,pady=(0,30))
        self.grid_f.columnconfigure((0,1,2),weight=1,uniform="sc")
        self.aggiorna()

    def aggiorna(self):
        for w in self.grid_f.winfo_children(): w.destroy()
        rows=leggi_dati()
        per_mac=defaultdict(lambda:{"lux":0,"db":0,"rows":[]})
        for r in rows:
            mac=r.get("mac_address","sconosciuto")
            if r.get("luce_lux") not in ("","None",None): per_mac[mac]["lux"]+=1
            if r.get("rumore_db") not in ("","None",None): per_mac[mac]["db"]+=1
            per_mac[mac]["rows"].append(r)
        for idx,(mac,data) in enumerate(per_mac.items()):
            row,col=divmod(idx,3)
            self._student_card(mac,data,row,col)

    def _student_card(self, mac, data, row, col):
        card=Card(self.grid_f); card.grid(row=row,column=col,padx=6,pady=6,sticky="ew")
        hf=ctk.CTkFrame(card,fg_color="transparent"); hf.pack(fill="x",padx=16,pady=(16,8))
        av=ctk.CTkFrame(hf,fg_color=C_ACCENT_BG,corner_radius=20,width=40,height=40); av.pack(side="left"); av.pack_propagate(False)
        ctk.CTkLabel(av,text="👤",font=ctk.CTkFont("Helvetica",18),text_color=C_ACCENT).place(relx=0.5,rely=0.5,anchor="center")
        ctk.CTkLabel(hf,text=mac[:17],font=ctk.CTkFont("Helvetica",13,weight="bold"),text_color=TEXT()).pack(side="left",padx=10)
        cf=ctk.CTkFrame(card,fg_color="transparent"); cf.pack(fill="x",padx=16,pady=(0,8))
        ctk.CTkLabel(cf,text=f"💡 {data['lux']} luminosity",font=ctk.CTkFont("Helvetica",11),text_color=SUBTEXT()).pack(side="left",padx=(0,12))
        ctk.CTkLabel(cf,text=f"🔊 {data['db']} noise",font=ctk.CTkFont("Helvetica",11),text_color=SUBTEXT()).pack(side="left")
        ctk.CTkFrame(card,fg_color=BORDER(),height=1).pack(fill="x")
        total=data["lux"]+data["db"]; label=f"View {total} measurement{'s' if total!=1 else ''}"
        exp={"open":False,"detail":None}
        def toggle(exp=exp,label=label):
            if exp["open"]:
                if exp["detail"]: exp["detail"].destroy(); exp["detail"]=None
                btn.configure(text=f"{label}  ∨"); exp["open"]=False
            else:
                df=ctk.CTkFrame(card,fg_color=BG(),corner_radius=0); df.pack(fill="x")
                for r in data["rows"][:5]:
                    ts=r.get("timestamp_pc","")[:16]; lux=r.get("luce_lux",""); db=r.get("rumore_db","")
                    if lux: ctk.CTkLabel(df,text=f"💡 {round(float(lux))} lux  —  {ts}",font=ctk.CTkFont("Helvetica",11),text_color=SUBTEXT()).pack(anchor="w",padx=16,pady=2)
                    if db:  ctk.CTkLabel(df,text=f"🔊 {round(float(db))} dB  —  {ts}",font=ctk.CTkFont("Helvetica",11),text_color=SUBTEXT()).pack(anchor="w",padx=16,pady=2)
                exp["detail"]=df; btn.configure(text=f"{label}  ∧"); exp["open"]=True
        btn=ctk.CTkButton(card,text=f"{label}  ∨",font=ctk.CTkFont("Helvetica",12),
            fg_color="transparent",hover_color=C_ACCENT_BG,text_color=SUBTEXT(),
            anchor="w",height=38,corner_radius=0,command=toggle)
        btn.pack(fill="x")

# ══════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════
class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BG(), **kw); self._build()

    def _build(self):
        ctk.CTkLabel(self,text="Settings",font=ctk.CTkFont("Helvetica",28,weight="bold"),text_color=TEXT()).pack(anchor="w",padx=30,pady=(30,2))
        ctk.CTkLabel(self,text="Configure your dashboard preferences",font=ctk.CTkFont("Helvetica",13),text_color=SUBTEXT()).pack(anchor="w",padx=30,pady=(0,20))

        # Appearance card
        ac=Card(self); ac.pack(fill="x",padx=30,pady=(0,16))
        ctk.CTkLabel(ac,text="Appearance",font=ctk.CTkFont("Helvetica",16,weight="bold"),text_color=TEXT()).pack(anchor="w",padx=24,pady=(20,4))
        ctk.CTkLabel(ac,text="Theme Mode",font=ctk.CTkFont("Helvetica",12),text_color=SUBTEXT()).pack(anchor="w",padx=24,pady=(4,10))

        btn_row=ctk.CTkFrame(ac,fg_color="transparent"); btn_row.pack(fill="x",padx=24,pady=(0,6))
        btn_row.columnconfigure((0,1),weight=1,uniform="tb")

        # Light button
        self.light_btn=ctk.CTkFrame(btn_row,
            fg_color=C_ACCENT_BG if not THEME["dark"] else CARD(),
            corner_radius=10,
            border_width=2,
            border_color=C_ACCENT if not THEME["dark"] else BORDER())
        self.light_btn.grid(row=0,column=0,padx=(0,8),sticky="ew",ipady=20)
        ctk.CTkLabel(self.light_btn,text="☀️",font=ctk.CTkFont("Helvetica",28)).pack(pady=(16,4))
        ctk.CTkLabel(self.light_btn,text="Light Mode",font=ctk.CTkFont("Helvetica",13,weight="bold"),text_color=TEXT()).pack(pady=(0,16))
        self.light_btn.bind("<Button-1>",lambda e: self._set_theme(False))
        for child in self.light_btn.winfo_children(): child.bind("<Button-1>",lambda e: self._set_theme(False))

        # Dark button
        self.dark_btn=ctk.CTkFrame(btn_row,
            fg_color=C_ACCENT_BG if THEME["dark"] else CARD(),
            corner_radius=10,
            border_width=2,
            border_color=C_ACCENT if THEME["dark"] else BORDER())
        self.dark_btn.grid(row=0,column=1,padx=(8,0),sticky="ew",ipady=20)
        ctk.CTkLabel(self.dark_btn,text="🌙",font=ctk.CTkFont("Helvetica",28)).pack(pady=(16,4))
        ctk.CTkLabel(self.dark_btn,text="Dark Mode",font=ctk.CTkFont("Helvetica",13,weight="bold"),text_color=TEXT()).pack(pady=(0,16))
        self.dark_btn.bind("<Button-1>",lambda e: self._set_theme(True))
        for child in self.dark_btn.winfo_children(): child.bind("<Button-1>",lambda e: self._set_theme(True))

        theme_name = "Dark" if THEME["dark"] else "Light"
        self.theme_lbl=ctk.CTkLabel(ac,text=f"Current theme: {theme_name}",
            font=ctk.CTkFont("Helvetica",12),text_color=C_ACCENT)
        self.theme_lbl.pack(anchor="w",padx=24,pady=(4,20))

        # General card
        gc=Card(self); gc.pack(fill="x",padx=30,pady=(0,30))
        ctk.CTkLabel(gc,text="General",font=ctk.CTkFont("Helvetica",16,weight="bold"),text_color=TEXT()).pack(anchor="w",padx=24,pady=(20,4))
        ctk.CTkLabel(gc,text="More settings coming soon...",font=ctk.CTkFont("Helvetica",12),text_color=SUBTEXT()).pack(anchor="w",padx=24,pady=(0,20))

    def _set_theme(self, dark: bool):
        THEME["dark"] = dark
        if APP_REF: APP_REF.applica_tema()

    def aggiorna(self): pass

# ══════════════════════════════════════════════════════════════════
# APP PRINCIPALE
# ══════════════════════════════════════════════════════════════════
class EcoMonitorApp(ctk.CTk):
    def __init__(self):
        global APP_REF
        super().__init__()
        APP_REF = self
        self.title("EcoMonitor"); self.geometry("1280x800"); self.minsize(1100,700)
        self.configure(fg_color=BG()); self._current=None; self._active_idx=0
        self._build()

    def _build(self):
        self.sb=ctk.CTkFrame(self,fg_color=SIDEBAR(),width=240,corner_radius=0,border_width=1,border_color=BORDER())
        self.sb.pack(side="left",fill="y"); self.sb.pack_propagate(False)
        self.logo=ctk.CTkLabel(self.sb,text="EcoMonitor",font=ctk.CTkFont("Helvetica",20,weight="bold"),text_color=TEXT())
        self.logo.pack(anchor="w",padx=24,pady=(28,32))
        menu=[
            ("📊  Overview",   self._show_overview),
            ("📋  Data Table", self._show_datatable),
            ("📍  Locations",  self._show_locations),
            ("👤  Students",   self._show_students),
            ("⚙️   Settings",   self._show_settings),
        ]
        self._btns=[]
        for label,cmd in menu:
            btn=ctk.CTkButton(self.sb,text=label,font=ctk.CTkFont("Helvetica",14),
                fg_color="transparent",hover_color=C_ACCENT_BG,text_color=TEXT(),
                anchor="w",height=44,corner_radius=10,command=cmd)
            btn.pack(fill="x",padx=12,pady=2); self._btns.append(btn)
        self.main=ctk.CTkFrame(self,fg_color=BG(),corner_radius=0)
        self.main.pack(side="left",fill="both",expand=True)
        self._show_overview()

    def applica_tema(self):
        """Ricarica l'intera UI con il nuovo tema."""
        self._active_idx_bak = self._active_idx
        # Aggiorna sidebar
        self.sb.configure(fg_color=SIDEBAR(), border_color=BORDER())
        self.logo.configure(text_color=TEXT())
        self.main.configure(fg_color=BG())
        self.configure(fg_color=BG())
        for btn in self._btns:
            btn.configure(text_color=TEXT(), hover_color=C_ACCENT_BG)
        # Ricarica schermata corrente
        screens = [self._show_overview, self._show_datatable, self._show_locations, self._show_students, self._show_settings]
        screens[self._active_idx]()

    def _set_active(self,idx):
        self._active_idx=idx
        for i,btn in enumerate(self._btns):
            if i==idx: btn.configure(fg_color=C_ACCENT_BG,text_color=C_ACCENT,font=ctk.CTkFont("Helvetica",14,weight="bold"))
            else:       btn.configure(fg_color="transparent",text_color=TEXT(),font=ctk.CTkFont("Helvetica",14))

    def _clear(self):
        for w in self.main.winfo_children(): w.destroy()
        if hasattr(self,"_rid"): self.after_cancel(self._rid)

    def _show(self, idx, cls, refresh=True):
        self._clear(); self._set_active(idx)
        self._current=cls(self.main); self._current.pack(fill="both",expand=True)
        if refresh: self._refresh()

    def _show_overview(self):  self._show(0, OverviewFrame)
    def _show_datatable(self): self._show(1, DataTableFrame)
    def _show_locations(self): self._show(2, LocationsFrame)
    def _show_students(self):  self._show(3, StudentsFrame)
    def _show_settings(self):  self._show(4, SettingsFrame, refresh=False)

    def _refresh(self):
        if self._current and self._current.winfo_exists():
            self._current.aggiorna()
            self._rid=self.after(5000, self._refresh)

if __name__ == "__main__":
    EcoMonitorApp().mainloop()
