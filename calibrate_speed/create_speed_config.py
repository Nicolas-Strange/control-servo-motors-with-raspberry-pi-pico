import json

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
    """ mean absolute error calculation between the real values and the calculated values"""
    y_p = model(params, x)

    return mean_squared_error(y, y_p)


def plot(x: list, y: list, y_p: list) -> None:
    fig = plt.figure()
    ax = fig.add_subplot()

    ax.scatter(x, y, s=60, color="dodgerblue", label="Real")
    ax.scatter(x, y_p, s=60, color="red", label="Predicted", marker="+")

    ax.set_xlabel('waiting time between each steps (ms)')
    ax.set_ylabel('Rotation speed (°/s)')

    ax.legend()

    plt.show()


def plot_3d(x: list, y: list, y_p: list) -> None:
    """ plot aa 3D graph """
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    cond = np.where(x[0] < 100)
    x_1 = x[1][cond]
    x_2 = x[0][cond]
    y_p_2 = y_p[cond]

    ax.scatter(x[0], x[1], y, s=60, color="dodgerblue", label="Real")
    ax.scatter(x_2, x_1, y_p_2, s=60, color="red", label="Predicted", marker="+")

    ax.set_xlabel('steps (°)')
    ax.set_ylabel('waiting time between each steps (ms)')
    ax.set_zlabel('Rotation speed (°/s)')

    ax.view_init(45, 0)
    ax.legend()

    plt.show()


def run():
    """ core method to perform the analysis """
    df = pd.read_csv("data/time_analysis_servo_raspberry_pico.csv")

    max_speed_servo_specs = 600

    df = df[df["rotation_speed(°/s)"] <= max_speed_servo_specs]
    df["waiting_time(ms)"] = df["waiting_time(s)"] * 1000
    params = [290, 2]
    values = []
    parameters = {}
    min_speed_all = max_speed_servo_specs
    max_speed_all = 0

    for i in range(1, df["steps"].max() + 1):
        val = df[df["steps"] == i]
        x = val["waiting_time(ms)"].to_numpy()
        y = val["rotation_speed(°/s)"].to_numpy()
        min_speed = y.min()
        max_speed = y.max()

        min_speed_all = min(min_speed_all, min_speed)
        max_speed_all = max(max_speed_all, max_speed)

        res = minimize(mse, np.array(params), args=(x, y), tol=1e-3)

        y_p = model(res.x, x)

        parameters[i] = {
            "min_speed": min_speed,
            "max_speed": max_speed,
            "params": list(res.x),
            "mae": f"{round(mean_absolute_error(y, y_p), 4)} degree/s"
        }

        values.extend([[i, x[ind - 1], y[ind - 1], y_p[ind - 1]] for ind in range(1, len(x) + 1)])
        # print(list(res.x))
        # plot(x, y, y_p)

    # Clean up unnecessary functions
    clean_parameters = {}

    max_step_all = max([int(i) for i in parameters.keys()])
    for step in range(1, max_step_all, 1):
        max_speed = parameters[step]["max_speed"]
        min_speed = parameters[step]["min_speed"]
        clean_parameters[step] = parameters[step]
        if min_speed <= max_speed_all <= max_speed:
            break

    name_servo = "servo_1"
    path_config = "../upload_to_raspberry_pi_pico/params/servo_params.json"
    config = load_json(path_config)
    config[name_servo]["speed_config"] = clean_parameters

    config[name_servo]["min_speed_d_s"] = min_speed_all
    config[name_servo]["max_speed_d_s"] = max_speed_all

    print(config)

    save_json(path=path_config, json_to_save=config)

    values = np.array(values)
    plot_3d([values[:, 0], values[:, 1]], values[:, 2], values[:, 3])


if __name__ == '__main__':
    run()
