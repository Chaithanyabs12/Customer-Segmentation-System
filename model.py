import pandas as pd
from sklearn.cluster import KMeans

def cluster_customers(data):
    df = pd.DataFrame(data)

    X = df[["Income", "Spending"]]

    # 🔥 Dynamic cluster fix
    k = min(3, len(df))

    kmeans = KMeans(n_clusters=k, random_state=42)
    df["Cluster"] = kmeans.fit_predict(X)

    return df