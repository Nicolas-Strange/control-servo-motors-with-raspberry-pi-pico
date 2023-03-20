import json
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error, mean_absolute_error


def load_json(path: str) -> dict:
    """
    load json param
    """
    with open(path) as infile:
        return json.load(infile)


def save_json(path: str, json_to_save: dict) -> None:
    """
    save json format file
    """
    with open(path, 'w') as outfile:
        json.dump(json_to_save, outfile, indent=4)


def model(params: list, x: list) -> list:
    """ custom model of the function to solve """
    return params[0] / x + params[1]


def mse(params: list, x: list, y: list) -> float:
    """ mean squared error calculation between the real values and the calculated values"""
    y_p = model(params, x)

    return mean_squared_error(y, y_p)


def plot(x: list, y: list, y_p: list) -> None:
    """ plot a 2D graph """
    fig = plt.figure()
    ax = fig.add_subplot()

    ax.scatter(x, y, s=60, color="dodgerblue", label="Real")
    ax.scatter(x, y_p, s=60, color="red", label="Predicted", marker="+")

    ax.set_xlabel('waiting time between each steps (ms)')
    ax.set_ylabel('Rotation speed (°/s)')

    ax.legend()

    plt.show()


def plot_3d(x: list, y: list, y_p: list) -> None:
    """ plot a 3D graph """
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    # cond = np.where(x[0] < 100)
    x_1 = x[1]
    x_2 = x[0]
    y_p_2 = y_p

    ax.scatter(x[0], x[1], y, s=60, color="dodgerblue", label="Real")
    ax.scatter(x_2, x_1, y_p_2, s=60, color="red", label="Predicted", marker="+")

    ax.set_xlabel('steps (°)')
    ax.set_ylabel('waiting time between each steps (ms)')
    ax.set_zlabel('Rotation speed (°/s)')

    ax.view_init(45, 0)
    ax.legend()

    plt.show()


def regression(x: np.array, y: np.array, params_model: list) -> Optional[tuple]:
    """ minimize the mean squared error between the real values and the predicted values"""
    try:
        res = minimize(mse, np.array(params_model), args=(x, y), tol=1e-3)
        y_p = model(res.x, x)
        mae = mean_absolute_error(y, y_p)
        return res, y_p, mae
    except Exception:
        return None, None, None


def clean_up_parameters(parameters: dict, max_speed_all: float, min_speed_all: float) -> dict:
    """
    clean up the parameters.
    We keep the steps for which there is the minimum speed value and the maximum speed value
    and then select the functions that fill the speed gap between them.
    """
    clean_parameters = {}

    lst_steps = [int(i) for i in parameters.keys()]
    lst_steps = sorted(lst_steps, reverse=True)

    def add(val: int):
        clean_parameters[val] = parameters[val]

    index_min = 360
    index_max = 0

    for key, value in parameters.items():
        if parameters[key]["max_speed"] == max_speed_all:
            index_max = key

        if parameters[key]["min_speed"] == min_speed_all:
            index_min = key

    add(index_min)
    add(index_max)

    max_speed_first = parameters[lst_steps[0]]["max_speed"]
    min_speed_last = parameters[lst_steps[-1]]["min_speed"]

    if min_speed_last < max_speed_first:
        return clean_parameters

    for step in lst_steps:
        if step in [index_min, index_max]:
            continue
        max_speed = parameters[step]["max_speed"]
        min_speed = parameters[step]["min_speed"]

        if max_speed > min_speed_last and min_speed < max_speed_first:
            add(step)
            break

    return clean_parameters


def build_params(df: pd.DataFrame, init_params_model: list, min_mae: float,
                 max_speed_servo_specs: int, plot_graph: bool = True) -> tuple:
    """ do the regression and save the parameters in a config"""

    values = []
    parameters = {}
    min_speed_all = max_speed_servo_specs
    max_speed_all = 0

    for i in df["steps"].unique():
        print(f"step: {i}")
        val = df[df["steps"] == i]
        x = val["waiting_time(ms)"].to_numpy()
        y = val["rotation_speed(°/s)"].to_numpy()

        res, y_p, mae = regression(x=x, y=y, params_model=init_params_model)
        mae = min_mae + 1 if mae is None else mae

        while mae > min_mae:
            x = x[:-1]
            y = y[:-1]

            res, y_p, mae = regression(x=x, y=y, params_model=init_params_model)

            is_none = mae
            mae = min_mae - 1 if mae is None else mae

            if is_none is None or mae > min_mae or len(x) <= 3:
                continue

            min_speed = y.min()
            max_speed = y.max()
            min_speed_all = round(min(min_speed_all, min_speed), 2)
            max_speed_all = round(max(max_speed_all, max_speed), 2)

            parameters[int(i)] = {
                "min_speed": round(min_speed, 2),
                "max_speed": round(max_speed, 2),
                "params": list(res.x),
                "mae": f"{round(mean_absolute_error(y, y_p), 4)} degree/s"
            }

            values.extend([[i, x[ind - 1], y[ind - 1], y_p[ind - 1]] for ind in range(1, len(x) + 1)])
        # plot(x, y, y_p)

    if plot_graph:
        values = np.array(values)
        plot_3d([values[:, 0], values[:, 1]], values[:, 2], values[:, 3])

    return parameters, max_speed_all, min_speed_all


def save_params(name_servo: str, clean_parameters: dict, path_config_load: str, path_config_saves: list,
                min_speed_all: float, max_speed_all: float):
    """ override the parameters """
    config_analysis = load_json(path_config_load)

    config_analysis[name_servo]["speed_config"] = clean_parameters
    del config_analysis[name_servo]["min_sleep_us"]
    del config_analysis[name_servo]["max_sleep_us"]

    config_analysis[name_servo]["min_speed_d_s"] = min_speed_all
    config_analysis[name_servo]["max_speed_d_s"] = max_speed_all

    for path_config_save in path_config_saves:
        config_final = load_json(path_config_save)
        config_final[name_servo] = config_analysis[name_servo]

        save_json(path=path_config_save, json_to_save=config_final)


def run():
    """ core method to perform the analysis """

    name_servo = "servo_s53_20"
    init_params_model = [24.36093280680071, 3.6269641385313385]
    max_speed_servo_specs = 600
    min_mae = 0.9

    path_config_load = "./upload_to_rpp_for_data_acquisition/params/servo_params.json"
    path_config_saves = [
        "../upload_to_raspberry_pi_pico/params/servo_params.json",
        "./upload_to_rpp_for_data_visualization/params/servo_params.json"
    ]

    df = pd.read_csv(f"data/time_analysis_raspberry_pico_{name_servo}.csv")

    df = df[df["rotation_speed(°/s)"] <= max_speed_servo_specs]
    df["waiting_time(ms)"] = df["waiting_time(s)"] * 1000

    parameters, max_speed_all, min_speed_all = \
        build_params(
            df=df, init_params_model=init_params_model, min_mae=min_mae,
            max_speed_servo_specs=max_speed_servo_specs, plot_graph=True
        )

    # Clean up unnecessary functions
    clean_parameters = \
        clean_up_parameters(parameters=parameters, max_speed_all=max_speed_all, min_speed_all=min_speed_all)

    save_params(
        name_servo=name_servo, clean_parameters=clean_parameters, path_config_load=path_config_load,
        path_config_saves=path_config_saves, min_speed_all=min_speed_all, max_speed_all=max_speed_all)


if __name__ == '__main__':
    run()
