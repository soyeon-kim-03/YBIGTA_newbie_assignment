import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_decision_boundary(model, X, y, title="Decision Boundary"):
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 300),
        np.linspace(y_min, y_max, 300),
    )
    grid = np.c_[xx.ravel(), yy.ravel()]
    Z = model.predict(grid).reshape(xx.shape)

    plt.figure(figsize=(6, 5))
    plt.contourf(xx, yy, Z, alpha=0.55, cmap=plt.cm.RdYlGn)
    plt.scatter(X[:, 0], X[:, 1], c=y, s=28, edgecolors="k", cmap=plt.cm.RdYlGn)
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.title(title)
    plt.show()


def plot_optimizer_histories(histories, x_axis="epoch", metric="val_loss", title=None):
    plt.figure(figsize=(8, 5))
    for name, history in histories.items():
        values = history.get(metric, [])
        if values:
            plt.plot(history[x_axis], values, label=name)
    plt.xlabel("Epoch" if x_axis == "epoch" else "Parameter update step")
    plt.ylabel(metric.replace("_", " ").title())
    plt.title(title or f"{metric} by {x_axis}")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.show()


def summarize(name, history):
    row = {
        "experiment": name,
        "updates": history["update_step"][-1],
        "elapsed_sec": history["elapsed_sec"][-1],
        "final_train_loss": history["train_loss"][-1],
        "final_train_acc": history["train_acc"][-1],
    }
    if history.get("val_loss"):
        row["final_val_loss"] = history["val_loss"][-1]
        row["final_val_acc"] = history["val_acc"][-1]
    return row


def result_table(named_histories):
    return pd.DataFrame([summarize(name, hist) for name, hist in named_histories.items()])
