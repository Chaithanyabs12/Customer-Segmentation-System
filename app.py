import pandas as pd
from flask import Flask, render_template, request, redirect, session
from model import cluster_customers

import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.secret_key = "secret123"

customer_data = []

# =========================
# LOGIN PAGE
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "chai" and password == "1216":
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # simple store (you can upgrade later to DB)
        return redirect("/")

    return render_template("register.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")


# =========================
# INPUT PAGE
# =========================
@app.route("/input")
def input_page():
    return render_template("input.html", data=customer_data)


# =========================
# ADD CUSTOMER
# =========================
@app.route("/add", methods=["POST"])
def add():
    age = int(request.form["age"])
    income = int(request.form["income"])
    spending = int(request.form["spending"])

    customer_data.append({
        "Age": age,
        "Income": income,
        "Spending": spending
    })

    return redirect("/input")


# =========================
# LOAD DATASET (NEW FEATURE)
# =========================
@app.route("/load_dataset")
def load_dataset():
    global customer_data

    # Load Excel dataset
    df = pd.read_excel("Mall_Customers(1).xlsx")

    # Rename columns
    df = df.rename(columns={
        "Annual Income (k$)": "Income",
        "Spending Score (1-100)": "Spending"
    })

    # Keep only required columns
    df = df[["Age", "Income", "Spending"]]

    # Convert to list
    customer_data = df.to_dict(orient="records")

    return redirect("/input")


# =========================
# RUN CLUSTERING + GRAPH + STATS
# =========================
@app.route("/run")
def run():
    if len(customer_data) < 2:
        return "⚠️ Add at least 2 customers"

    df = cluster_customers(customer_data)

    # LABELS
    label_map = {
        0: "📉 Budget Customers",
        1: "💰 High Spenders",
        2: "⭐ Premium Customers"
    }

    df["Label"] = df["Cluster"].map(label_map)

    # SCATTER GRAPH
    plt.figure(figsize=(5,4))
    colors = ['red', 'green', 'blue']

    for i in df["Cluster"].unique():
        subset = df[df["Cluster"] == i]
        plt.scatter(
            subset["Income"],
            subset["Spending"],
            color=colors[i % len(colors)],
            label=label_map.get(i, f"Cluster {i}"),
            s=100
        )

    plt.xlabel("Income")
    plt.ylabel("Spending Score")
    plt.title("Customer Segmentation")
    plt.legend()

    img1 = io.BytesIO()
    plt.savefig(img1, format='png', bbox_inches='tight')
    img1.seek(0)
    plot_url = base64.b64encode(img1.getvalue()).decode()
    plt.close()

    # PIE CHART
    plt.figure(figsize=(4,4))
    df["Label"].value_counts().plot.pie(autopct='%1.1f%%')
    plt.title("Cluster Distribution")

    img2 = io.BytesIO()
    plt.savefig(img2, format='png', bbox_inches='tight')
    img2.seek(0)
    pie_url = base64.b64encode(img2.getvalue()).decode()
    plt.close()

    # STATS
    total = len(df)
    avg_income = round(df["Income"].mean(), 2)
    avg_spending = round(df["Spending"].mean(), 2)

    data = df.to_dict(orient="records")

    return render_template(
        "result.html",
        data=data,
        plot_url=plot_url,
        pie_url=pie_url,
        total=total,
        avg_income=avg_income,
        avg_spending=avg_spending
    )


# =========================
# DELETE CUSTOMER
# =========================
@app.route("/delete/<int:index>")
def delete(index):
    if 0 <= index < len(customer_data):
        customer_data.pop(index)
    return redirect("/input")


# =========================
# CLEAR ALL DATA
# =========================
@app.route("/reset")
def reset():
    global customer_data
    customer_data = []
    return redirect("/input")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)