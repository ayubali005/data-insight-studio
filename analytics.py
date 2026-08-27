import ast, io, re, contextlib
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BLOCKED={'os','sys','subprocess','socket','pathlib','shutil','requests','urllib','httpx','ftplib'}

def validate_code(code):
    tree=ast.parse(code, mode='exec')
    for node in ast.walk(tree):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            names=[a.name.split('.')[0] for a in node.names]
            if any(n in BLOCKED for n in names): raise ValueError('Blocked import detected')
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in {'open','eval','exec','compile','__import__'}:
            raise ValueError(f'Blocked function: {node.func.id}')
    return True

def run_code(code, frames):
    validate_code(code)
    plt.close('all')
    ns={'pd':pd,'plt':plt,'__builtins__':{'len':len,'min':min,'max':max,'sum':sum,'round':round,'sorted':sorted,'abs':abs,'range':range,'str':str,'int':int,'float':float}}
    ns.update(frames)
    out=io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(code,'<ai-analysis>','exec'),ns,ns)
    result=ns.get('result')
    fig=plt.gcf() if plt.get_fignums() else None
    return result,out.getvalue(),fig

def fallback(question, frames):
    q=question.lower()
    name=list(frames)[0]
    df=frames[name]
    nums=df.select_dtypes('number').columns.tolist()
    # groupby mean/sum/count
    group=re.search(r'(?:by|per)\s+([\w ]+)',q)
    col=None
    for c in df.columns:
        if c.lower() in q: col=c; break
    if any(x in q for x in ['average','mean']) and group:
        g=next((c for c in df.columns if c.lower()==group.group(1).strip()), None)
        v=col if col and pd.api.types.is_numeric_dtype(df[col]) else (nums[0] if nums else None)
        if g and v:
            result=df.groupby(g)[v].mean().sort_values(ascending=False).reset_index(name=f'avg_{v}')
            ax=result.plot(kind='bar',x=g,y=f'avg_{v}',legend=False,title=f'Average {v} by {g}')
            ax.figure.tight_layout(); return result, f'Fallback: mean of {v} grouped by {g}.', ax.figure, f"result = {name}.groupby('{g}')['{v}'].mean().sort_values(ascending=False).reset_index(name='avg_{v}')"
    if 'correlation' in q and len(nums)>=2:
        a,b=nums[:2]; value=float(df[a].corr(df[b])); return pd.DataFrame({'metric':['correlation'],'value':[value]}), f'Correlation between {a} and {b}: {value:.3f}', None, f"result = pd.DataFrame({{'metric':['correlation'],'value':[{name}['{a}'].corr({name}['{b}'])]}})"
    if any(x in q for x in ['count','how many','number of rows']):
        result=pd.DataFrame({'metric':['rows'],'value':[len(df)]}); return result, f'{len(df):,} rows.', None, f"result = pd.DataFrame({{'metric':['rows'],'value':[len({name})]}})"
    if any(x in q for x in ['sum','total']) and group:
        g=next((c for c in df.columns if c.lower()==group.group(1).strip()), None)
        v=col if col and pd.api.types.is_numeric_dtype(df[col]) else (nums[0] if nums else None)
        if g and v:
            result=df.groupby(g)[v].sum().sort_values(ascending=False).reset_index(name=f'total_{v}')
            ax=result.plot(kind='bar',x=g,y=f'total_{v}',legend=False,title=f'Total {v} by {g}'); ax.figure.tight_layout()
            return result, f'Total {v} grouped by {g}.', ax.figure, f"result = {name}.groupby('{g}')['{v}'].sum().sort_values(ascending=False).reset_index(name='total_{v}')"
    result=df.head(10); return result, f"Showing a preview of {name}. Add an API key for richer natural-language analysis.", None, f'result = {name}.head(10)'
