#%%
import pandas as pd
import itertools

# Load data and prepare df
def load_data(filename, cols_names, variants_names, reference, remove_mean_ref=True):
    df_orig = pd.read_csv(filename, index_col=[0, 1])
    df_orig = df_orig.replace(variants_names)
    df_orig = df_orig.rename(columns=cols_names)
    values = list(cols_names.values())
    variants = list(variants_names.values())
    df_orig = df_orig.pivot(columns="variant", values=values)[itertools.product(values, variants)]
    tmp = df_orig.groupby(level=0).mean()
    tmp["design"] = "￿"
    tmp = tmp.reset_index().set_index(["tech", "design"])
    if (remove_mean_ref):
        tmp[[col for col in tmp.columns if col[1]==reference]] = "-"
    df_orig = pd.concat([df_orig, tmp]).sort_index()
    return df_orig.reset_index().replace({"￿": "Média"}).set_index(["tech", "design"])

def format_data(dif_csv, raw_csv, cols_names, variants_names, reference, formatter_abs, formatter_percentage, use_comma_as_sep, best_small):
    df_orig = load_data(dif_csv, cols_names, variants_names, reference)
    df_raw = load_data(raw_csv, cols_names, variants_names, reference)
    df = df_orig.copy()

    # Format data into strings
    if use_comma_as_sep:
        formatter = lambda f: (lambda x: f(x).replace(',',';').replace('.',',').replace(';','.') if type(x) != str and not pd.isna(x) else x)
    else:
        formatter = lambda f: (lambda x: f(x) if type(x) != str and not pd.isna(x) else x)
    formatters = {
        (metric, reference): formatter(format) for metric, format in formatter_abs.items()
    }
    variants = list(variants_names.values())
    variants.remove(reference)
    for col in (itertools.product(list(cols_names.values()), variants)):
        formatters[col] = formatter(lambda x: formatter_percentage(x*100 if type(x) != str else x))
    for col, func in formatters.items():
        df[col] = df[col].apply(func)

    # Fill NAN
    df = df.mask(df_raw.isna(), lambda x: "NF").fillna(df_raw)
    for col in (itertools.product(list(cols_names.values()), variants)):
        df[col] = df[col].apply(formatter(formatter_abs[col[0]]))
    
    # make the best result bold
    def mark_best(line):
        pivoted = line.reset_index().set_index("level_0").pivot(columns="variant", values=line.name)
        for col, small in best_small.items():
            if small:
                best_val = pivoted.loc[col].min()
            else:
                best_val = pivoted.loc[col].max()
            pivoted.loc[col] = pivoted.loc[col].apply(lambda x: x == best_val)
        pivoted = pivoted.loc[best_small.keys()]
        unpivoted = pivoted.stack()
        unpivoted.name = line.name
        unpivoted.reset_index()
        return unpivoted
    df_copy = df_orig.copy()
    df_copy.loc[:, (slice(None), reference)] = 0
    df_copy = df_copy.mask(df_raw.isna(), lambda x: pd.NA).fillna(df_raw)
    best = df_copy.apply(mark_best, axis=1).loc[df.index, df.columns]
    df = df.mask(best.values, lambda x: "\\textbf{"+x+"}")

    # Convert to latex table
    table = df.to_latex(multicolumn_format='c|',
                        column_format='ll'+'|rrr'*len(cols_names))

    lines = []
    for i in table.split('\n'):
        if i.startswith("\cline"):
            lines.insert(-1, "\cdashline{2-"+str(df.shape[1]+2)+"}")
        lines.append(i)
    header = lines[2].split("&")
    header[-1] = header[-1].replace("c|", "c")
    lines[2] = "&".join(header)
    del lines[1]
    return "\n".join(lines)

# Global
variants_names = {"ref": "RePlAce-ref", "epl3": "ePlace", "base": "RePlAce"}
reference = "RePlAce-ref"
use_comma_as_sep = True
formatter_percentage = "{:0,.1f}\%".format

#%% GPL
def gpl():
    dif_csv = "results/place_gp_diff.csv"
    raw_csv = "results/place_gp.csv"
    cols_names = {
        'final_hpwl': 'HPWL ($\mu$m)',
        'fmax': 'Frequência máxima (MHz)',
        #'max_iter': 'Iterações',
        'cpu_time_user': 'Tempo de execução (s)'}
    formatter_abs = {
        'HPWL ($\mu$m)': "{:0,.0f}".format,
        'Frequência máxima (MHz)': lambda x: "{:0,.0f}".format(x/1000000),
        #'Iterações': "{:0,.0f}".format,
        'Tempo de execução (s)': "{:0,.0f}".format
    }
    best_small = {
        'HPWL ($\mu$m)': True, 
        'Frequência máxima (MHz)': False,
        #'Iterações': True,
        'Tempo de execução (s)': True
    }

    return format_data(
        dif_csv,
        raw_csv,
        cols_names,
        variants_names,
        reference,
        formatter_abs,
        formatter_percentage,
        use_comma_as_sep,
        best_small)
with open("results/table_gp.tex", 'w') as f:
    f.write(gpl())

#%%
def dpl():
    dif_csv = "results/place_dp_diff.csv"
    raw_csv = "results/place_dp.csv"
    cols_names = {
        'final_hpwl': 'HPWL ($\mu$m)',
        'fmax': 'Frequência máxima (MHz)',
        'total_displacement': 'Deslocamento total ($\mu$m)'}
    formatter_abs = {
        'HPWL ($\mu$m)': "{:0,.0f}".format,
        'Frequência máxima (MHz)': lambda x: "{:0,.0f}".format(x/1000000),
        'Deslocamento total ($\mu$m)': "{:0,.0f}".format
    }
    best_small = {
        'HPWL ($\mu$m)': True, 
        'Frequência máxima (MHz)': False,
        'Deslocamento total ($\mu$m)': True
    }

    return format_data(
        dif_csv,
        raw_csv,
        cols_names,
        variants_names,
        reference,
        formatter_abs,
        formatter_percentage,
        use_comma_as_sep,
        best_small)
with open("results/table_dp.tex", 'w') as f:
    f.write(dpl())

#%%
def final():
    dif_csv = "results/final_diff.csv"
    raw_csv = "results/final.csv"
    cols_names = {
        'power': 'Potência (mW)',
        'fmax': 'Frequência máxima (MHz)',
        'area': 'Área de instâncias ($\mu$m$^2$)'}
    formatter_abs = {
        'Potência (mW)': lambda x: "{:0,.0f}".format(x*1000),
        'Frequência máxima (MHz)': lambda x: "{:0,.0f}".format(x/1000000),
        'Área de instâncias ($\mu$m$^2$)': "{:0,.0f}".format
    }
    best_small = {
        'Potência (mW)': True, 
        'Frequência máxima (MHz)': False,
        'Área de instâncias ($\mu$m$^2$)': True
    }

    return format_data(
        dif_csv,
        raw_csv,
        cols_names,
        variants_names,
        reference,
        formatter_abs,
        formatter_percentage,
        use_comma_as_sep,
        best_small)
with open("results/table_final.tex", 'w') as f:
    f.write(final())

# %%
