import os, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
from llm_client import LLMClient
from analytics import run_code, fallback

# Pillow is only used for displaying saved charts when available.

class App:
    def __init__(self, root):
        self.root=root; root.title('Data Insight Studio'); root.geometry('1120x760')
        self.frames={}; self.last_photo=None; self.client=LLMClient()
        self.build()
    def build(self):
        top=ttk.Frame(self.root,padding=10); top.pack(fill='x')
        ttk.Button(top,text='Add CSV/XLSX',command=self.load).pack(side='left')
        ttk.Label(top,text='Ask a question:').pack(side='left',padx=(18,5))
        self.q=tk.StringVar(); ttk.Entry(top,textvariable=self.q,width=70).pack(side='left',fill='x',expand=True)
        ttk.Button(top,text='Analyze',command=self.analyze).pack(side='left',padx=8)
        body=ttk.Panedwindow(self.root,orient='horizontal'); body.pack(fill='both',expand=True,padx=10,pady=5)
        left=ttk.Frame(body,padding=8); right=ttk.Frame(body,padding=8); body.add(left,weight=1); body.add(right,weight=3)
        ttk.Label(left,text='Loaded datasets',font=('TkDefaultFont',11,'bold')).pack(anchor='w')
        self.list=tk.Listbox(left,height=18); self.list.pack(fill='both',expand=True,pady=5)
        self.meta=tk.Text(left,height=12,wrap='word'); self.meta.pack(fill='both',expand=True)
        ttk.Label(right,text='Result').pack(anchor='w')
        self.result=tk.Text(right,height=13,wrap='none'); self.result.pack(fill='both',expand=True)
        tabs=ttk.Notebook(right); tabs.pack(fill='both',expand=True,pady=(8,0))
        code_frame=ttk.Frame(tabs); summary_frame=ttk.Frame(tabs); tabs.add(code_frame,text='Generated Code'); tabs.add(summary_frame,text='Summary')
        self.code=tk.Text(code_frame,wrap='none'); self.code.pack(fill='both',expand=True)
        self.summary=tk.Text(summary_frame,wrap='word'); self.summary.pack(fill='both',expand=True)
    def load(self):
        files=filedialog.askopenfilenames(filetypes=[('Data files','*.csv *.xlsx *.xls')])
        for f in files:
            try:
                df=pd.read_csv(f) if Path(f).suffix.lower()=='.csv' else pd.read_excel(f)
                name=Path(f).stem; base=name; i=2
                while name in self.frames: name=f'{base}_{i}'; i+=1
                self.frames[name]=df; self.list.insert('end',name)
                self.meta.insert('end',f'{name}: {df.shape[0]} rows x {df.shape[1]} cols\n{df.dtypes.astype(str).to_dict()}\n\n')
            except Exception as e: messagebox.showerror('Load error',str(e))
    def analyze(self):
        if not self.frames: return messagebox.showwarning('No data','Load at least one dataset.')
        q=self.q.get().strip()
        if not q: return messagebox.showwarning('Question missing','Enter an analysis question.')
        schemas={k: f"columns={list(v.columns)}, dtypes={v.dtypes.astype(str).to_dict()}, rows={len(v)}" for k,v in self.frames.items()}
        try:
            generated=self.client.generate(q,schemas)
            if generated:
                code=generated.get('code',''); explanation=generated.get('explanation','')
                result,stdout,fig=run_code(code,self.frames)
                self.code.delete('1.0','end'); self.code.insert('1.0',code)
                self.summary.delete('1.0','end'); self.summary.insert('1.0',explanation+'\n\n'+stdout)
            else:
                result,explanation,fig,code=fallback(q,self.frames)
                self.code.delete('1.0','end'); self.code.insert('1.0',code)
                self.summary.delete('1.0','end'); self.summary.insert('1.0',explanation)
            self.result.delete('1.0','end'); self.result.insert('1.0',result.to_string(index=False) if hasattr(result,'to_string') else str(result))
            if fig:
                path=Path('.analysis_cache'); path.mkdir(exist_ok=True); img=path/'latest.png'; fig.savefig(img,dpi=120,bbox_inches='tight'); self.show_image(img)
        except Exception as e:
            messagebox.showerror('Analysis failed',str(e))
    def show_image(self,path):
        # Open in the platform image viewer rather than embedding a large image in Tkinter.
        try:
            if os.name=='nt': os.startfile(path)
        except Exception: pass

if __name__=='__main__':
    # Pillow is optional; the application does not require it.
    root=tk.Tk(); App(root); root.mainloop()
