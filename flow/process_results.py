#%%
import os
import re
import pandas as pd
import json

data = {
    "variant": [],
    "tech": [],
    "design": [],
    "skip_io": [],
    "place_gp": [],
    "place_dp": [],
    "cts": [],
    "grt": [],
    "route": [],
    "final": []
}


def addData(variant, tech, design, skip_io, place_gp, place_dp, cts, grt, route, final):
    data["variant"].append(variant)
    data["tech"].append(tech)
    data["design"].append(design)
    data["skip_io"].append(skip_io)
    data["place_gp"].append(place_gp)
    data["place_dp"].append(place_dp)
    data["cts"].append(cts)
    data["grt"].append(grt)
    data["route"].append(route)
    data["final"].append(final)

designs = []
with open("tests.txt") as f:
  for line in f:
    designs.append(tuple(line.strip().split('/', 1)))

for tech, design in designs:
    if design == "black_parrot":
        design = "bp"
    print(tech, design)
    for variant in os.listdir(os.path.join("logs", tech, design)):
        if variant == 'epl':
            continue
        if variant == 'epl2':
            continue
        files = {
            "skip_io": os.path.join("logs", tech, design, variant, "3_1_place_gp_skip_io.log"),
            "place_gp": os.path.join("logs", tech, design, variant, "3_3_place_gp.log"),
            "place_dp": os.path.join("logs", tech, design, variant, "3_5_place_dp.log"),
            "cts": os.path.join("logs", tech, design, variant, "4_1_cts.log"),
            "grt": os.path.join("logs", tech, design, variant, "5_1_grt.log"),
            "route": os.path.join("logs", tech, design, variant, "5_2_route.log"),
            "final": os.path.join("logs", tech, design, variant, "6_report.log")
        }
        for step, file in files.items():
            if not os.path.isfile(file):
                print("not found", file)
                files[step] = None
        addData(variant, tech, design, **files)
data = pd.DataFrame(data)

run_info = data.set_index(["tech", "design", "variant"]).sort_index(ascending=[True, True, False])
def verify_data(file):
    if not file:
        return None
    json_file = file[:-3]+"json";
    if not os.path.isfile(json_file):
        return "NOT FINISHED"
    with open(json_file) as file:
        data = json.load(file)
    for key in data:
        if key.endswith("errors__count"):
            if data[key] == 0:
                return "OK"
            else:
                return "FAILED"
    
run_info = run_info.map(verify_data)
run_info.to_csv("results/has_data.csv")
print(run_info)

def get_fmax(file):
    if not file:
        return None
    json_file = file[:-3]+"json";
    if not os.path.isfile(json_file):
        return "NOT FINISHED"
    with open(json_file) as file:
        data = json.load(file)
    timing_fmax = "OK"
    for key in data:
        if key == "timeout":
            if data[key] != 0:
                return "TIMEOUT"
        if key.endswith("errors__count"):
            if data[key] != 0:
                timing_fmax = "FAILED"
        if key.endswith("timing__fmax"):
            if timing_fmax != "FAILED":
                timing_fmax = data[key]
    return timing_fmax
fmax_data = data.set_index(["tech", "design", "variant"]).sort_index(ascending=[True, True, False])
fmax_data = fmax_data.map(get_fmax)
fmax_data.to_csv("results/fmax_data.csv")
print(fmax_data)
        
#%%
def process_gp_log(filename):
    final_hpwl = None
    final_area = None
    max_iter = None
    final_overflow = None
    cpu_time_user = None
    cpu_time_sys = None
    peak_memory = None

    if filename:
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("[INFO GPL-1001]"):
                    if max_iter:
                        raise ValueError(
                            f"max_iter is already {max_iter}. File: {filename}"
                        )
                    max_iter = int(line.split()[-1].strip())

                splitted = line.split()
                if len(splitted) == 9:
                    if splitted[1] == splitted[3] == splitted[5] == splitted[6] == splitted[8] == '|':
                        if final_overflow:
                            raise ValueError(
                                f"final_overflow is already {final_overflow}. File: {filename}"
                            )
                        final_overflow = float(splitted[2].strip())

                if line.startswith("[INFO EPL-0020]"):
                    if max_iter:
                        raise ValueError(
                            f"max_iter is already {max_iter}. File: {filename}"
                        )
                    max_iter = int(line.split()[2].strip())
                    if final_overflow:
                        raise ValueError(
                            f"final_overflow is already {final_overflow}. File: {filename}"
                        )
                    final_overflow = float(line.split()[4].strip()[:-1])/100.0

                if line.startswith("final hpwl: "):
                    if final_hpwl:
                        raise ValueError(
                            f"final_hpwl is already {final_hpwl}. File: {filename}"
                        )
                    final_hpwl = float(line.split()[-2].strip())

                if line.startswith("Design area"):
                    if final_area:
                        raise ValueError(
                            f"final_area is already {final_area}. File: {filename}"
                        )
                    final_area = int(line.split()[2].strip())

                if line.startswith("Elapsed time:"):
                    if cpu_time_user:
                        raise ValueError(
                            f"cpu_time_user is already {cpu_time_user}. File: {filename}"
                        )
                    cpu_time_user = float(line.split()[6].strip())
                    if cpu_time_sys:
                        raise ValueError(
                            f"cpu_time_sys is already {cpu_time_sys}. File: {filename}"
                        )
                    cpu_time_sys = float(line.split()[8].strip())
                    if peak_memory:
                        raise ValueError(
                            f"peak_memory is already {peak_memory}. File: {filename}"
                        )
                    peak_memory = line.split()[-1].strip()[:-1]

    return {
        "final_hpwl": final_hpwl,
        "final_area": final_area,
        "max_iter": max_iter,
        "final_overflow": final_overflow,
        "cpu_time_user": cpu_time_user,
        "cpu_time_sys": cpu_time_sys,
        "peak_memory": peak_memory
    }
    
def process_gp_log_all(filename):
    data = {}
    json_file = filename[:-3]+"json" if filename else ""
    if os.path.isfile(json_file):
        with open(json_file) as file:
            data = json.load(file)
    get_value = lambda key: data[key] if key in data else None
    final_data = {
        "final_hpwl": None,
        "final_area": None,
        "setup_tns": get_value("globalplace__timing__setup__tns"),
        "setup_ws": get_value("globalplace__timing__setup__ws"),
        "hold_tns": get_value("globalplace__timing__hold__tns"),
        "hold_ws": get_value("globalplace__timing__hold__ws"),
        "fmax": get_value("globalplace__timing__fmax"),
        "power": get_value("globalplace__power__total"),
        "utilization": get_value("globalplace__design__instance__utilization"),
        "max_iter": None
    }
    
    temp = process_gp_log(filename)
    return final_data | temp

def process_dpl_log(filename):
    legalized_hpwl = None
    final_hpwl = None
    cpu_time_user = None
    cpu_time_sys = None
    peak_memory = None

    if filename:
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("legalized HPWL"):
                    if legalized_hpwl:
                        raise ValueError(
                            f"legalized_hpwl is already {legalized_hpwl}. File: {filename}"
                        )
                    legalized_hpwl = float(line.split()[2].strip())
                if line.startswith("[INFO DPL-0022]"):
                    if final_hpwl:
                        raise ValueError(
                            f"final_hpwl is already {final_hpwl}. File: {filename}"
                        )
                    final_hpwl = float(line.split()[4].strip())
                if line.startswith("Elapsed time:"):
                    if cpu_time_user:
                        raise ValueError(
                            f"cpu_time_user is already {cpu_time_user}. File: {filename}"
                        )
                    cpu_time_user = float(line.split()[6].strip())
                    if cpu_time_sys:
                        raise ValueError(
                            f"cpu_time_sys is already {cpu_time_sys}. File: {filename}"
                        )
                    cpu_time_sys = float(line.split()[8].strip())
                    if peak_memory:
                        raise ValueError(
                            f"peak_memory is already {peak_memory}. File: {filename}"
                        )
                    peak_memory = line.split()[-1].strip()[:-1]

    data = {}
    json_file = filename[:-3]+"json" if filename else ""
    if os.path.isfile(json_file):
        with open(json_file) as file:
            data = json.load(file)
    get_value = lambda key: data[key] if key in data else None
    return {
        "legalized_hpwl": legalized_hpwl,
        "final_hpwl": final_hpwl,
        "total_displacement": get_value("detailedplace__design__instance__displacement__total"),
        "mean_displacement": get_value("detailedplace__design__instance__displacement__mean"),
        "max_displacement": get_value("detailedplace__design__instance__displacement__max"),
        "setup_tns": get_value("detailedplace__timing__setup__tns"),
        "setup_ws": get_value("detailedplace__timing__setup__ws"),
        "hold_tns": get_value("detailedplace__timing__hold__tns"),
        "hold_ws": get_value("detailedplace__timing__hold__ws"),
        "fmax": get_value("detailedplace__timing__fmax"),
        "power": get_value("detailedplace__power__total"),
        "utilization": get_value("detailedplace__design__instance__utilization"),
        "stdcell_count": get_value("detailedplace__design__instance__count__stdcell"),
        "macro_count": get_value("detailedplace__design__instance__count__macros"),
        "cpu_time_user": cpu_time_user,
        "cpu_time_sys": cpu_time_sys,
        "peak_memory": peak_memory,
    }
    
def process_final_log(filename):
    cpu_time_user = None
    cpu_time_sys = None
    peak_memory = None

    if filename:
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("Elapsed time:"):
                    if cpu_time_user:
                        raise ValueError(
                            f"cpu_time_user is already {cpu_time_user}. File: {filename}"
                        )
                    cpu_time_user = float(line.split()[6].strip())
                    if cpu_time_sys:
                        raise ValueError(
                            f"cpu_time_sys is already {cpu_time_sys}. File: {filename}"
                        )
                    cpu_time_sys = float(line.split()[8].strip())
                    if peak_memory:
                        raise ValueError(
                            f"peak_memory is already {peak_memory}. File: {filename}"
                        )
                    peak_memory = line.split()[-1].strip()[:-1]

    data = {}
    json_file = filename[:-3]+"json" if filename else ""
    if os.path.isfile(json_file):
        with open(json_file) as file:
            data = json.load(file)
    get_value = lambda key: data[key] if key in data else None
    return {
        "setup_tns": get_value("finish__timing__setup__tns"),
        "setup_ws": get_value("finish__timing__setup__ws"),
        "hold_tns": get_value("finish__timing__hold__tns"),
        "hold_ws": get_value("finish__timing__hold__ws"),
        "fmax": get_value("finish__timing__fmax"),
        "power": get_value("finish__power__total"),
        "utilization": get_value("finish__design__instance__utilization"),
        "stdcell_count": get_value("finish__design__instance__count__stdcell"),
        "macro_count": get_value("finish__design__instance__count__macros"),
        "area": get_value("finish__design__instance__area"),
        "cpu_time_user": cpu_time_user,
        "cpu_time_sys": cpu_time_sys,
        "peak_memory": peak_memory,
    }

skip_io_data = []
place_gp_data = []
place_dp_data = []
final_data = []
for file in data.itertuples(False):
    skip_io_data.append(process_gp_log(file.skip_io))
    skip_io_data[-1]["variant"] = file.variant
    skip_io_data[-1]["tech"] = file.tech
    skip_io_data[-1]["design"] = file.design

    place_gp_data.append(process_gp_log_all(file.place_gp))
    place_gp_data[-1]["variant"] = file.variant
    place_gp_data[-1]["tech"] = file.tech
    place_gp_data[-1]["design"] = file.design
    
    place_dp_data.append(process_dpl_log(file.place_dp))
    place_dp_data[-1]["variant"] = file.variant
    place_dp_data[-1]["tech"] = file.tech
    place_dp_data[-1]["design"] = file.design
    
    final_data.append(process_final_log(file.final))
    final_data[-1]["variant"] = file.variant
    final_data[-1]["tech"] = file.tech
    final_data[-1]["design"] = file.design

skip_io_df = pd.DataFrame(skip_io_data).set_index(["tech", "design", "variant"]).sort_index(ascending=[True, True, False])
skip_io_df.to_csv("./results/skip_io.csv")
print(skip_io_df)
place_gp_df = pd.DataFrame(place_gp_data).set_index(["tech", "design", "variant"]).sort_index(ascending=[True, True, False])
place_gp_df.to_csv("./results/place_gp.csv")
print(place_gp_df)
place_dp_df = pd.DataFrame(place_dp_data).set_index(["tech", "design", "variant"]).sort_index(ascending=[True, True, False])
place_dp_df.to_csv("./results/place_dp.csv")
print(place_dp_df)
final_df = pd.DataFrame(final_data).set_index(["tech", "design", "variant"]).sort_index(ascending=[True, True, False])
final_df.to_csv("./results/final.csv")
print(final_df)

def generate_diff(df):
    ref = df[df.index.get_level_values('variant') == 'ref']
    if (ref.shape[0] > 1):
        raise ValueError(f"ref error in {df}")
    if (ref.shape[0]==0):
        return
    new_df = pd.DataFrame(index=df.index, columns=df.columns)
    for idx in new_df.index:
        for col in df:
            if idx[2] == "ref":
                new_df.loc[idx, col] = df.loc[idx, col]
            else:
                ref = df.loc[(idx[0], idx[1], "ref"), col]
                variant = df.loc[idx, col]
                if df.loc[(idx[0], idx[1], ["ref", idx[2]]), col].isna().any():
                    continue
                if col == "peak_memory":
                    ref = int(ref[:-2])
                    variant = int(variant[:-2])
                new_df.loc[idx, col] = (variant - ref)/abs(ref)
    return new_df

skip_io_df_diff = skip_io_df.groupby(["tech", "design"], group_keys=False).apply(generate_diff)
skip_io_df_diff.to_csv("./results/skip_io_diff.csv")
place_gp_df_diff = place_gp_df.groupby(["tech", "design"], group_keys=False).apply(generate_diff)
place_gp_df_diff.to_csv("./results/place_gp_diff.csv")
place_dp_df_diff = place_dp_df.groupby(["tech", "design"], group_keys=False).apply(generate_diff)
place_dp_df_diff.to_csv("./results/place_dp_diff.csv")
final_df_diff = final_df.groupby(["tech", "design"], group_keys=False).apply(generate_diff)
final_df_diff.to_csv("./results/final_diff.csv")