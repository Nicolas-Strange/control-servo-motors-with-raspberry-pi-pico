import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression


def plot(x: list, y: list, y_p: list, text: str) -> None:
    fig = plt.figure()
    ax = fig.add_subplot()

    ax.scatter(x, y, s=40, color="orange", label="Real")
    ax.plot(x, y_p, color='k')

    ax.set_xlabel('Percentage rotation speed (%)')
    ax.set_ylabel('Rotation speed (°/s)')

    ax.text(0, 500, text, fontsize=12)

    plt.show()


def run():
    """ core method to perform the analysis """
    df = pd.read_csv("data/data_rotation_results.csv")

    x = df.iloc[:, :-1].values
    y = df.iloc[:, 1].values

    regr = LinearRegression()
    regr.fit(x, y)

    y_p = regr.predict(x)
    rho = np.corrcoef([i[0] for i in x], y)

    res = f"rotation_speed = {round(regr.coef_[0], 2)} * percent_speed + {round(regr.intercept_, 2)} " \
          f"\nPearson = {round(rho[0, 1], 4)}"

    print(res)

    plot(x, y, y_p, res)


if __name__ == '__main__':
    run()
