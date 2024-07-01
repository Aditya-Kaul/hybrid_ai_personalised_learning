import numpy as np
import matplotlib.pyplot as plt

from io import BytesIO
import base64

from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.datasets import make_classification
from sklearn.decomposition import PCA
from sklearn.datasets import make_blobs
from sklearn.svm import SVC

def generate_linear_regression_plot():
    # Generate sample data
    np.random.seed(42)
    X = np.linspace(0, 10, 100).reshape(-1, 1)
    y = 2 * X + 1 + np.random.randn(100, 1) * 2

    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(X, y, color='blue', alpha=0.7, label='Data points')
    ax.plot(X, model.predict(X), color='red', label='Regression line')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Linear Regression')
    ax.legend()

    # Save plot to buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"

def generate_kmeans_plot():
    # Generate sample data
    np.random.seed(42)
    X = np.random.randn(300, 2) * 2
    X[:100, 0] += 6
    X[:100, 1] += 4

    fig, axs = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle('K-means Clustering Steps', fontsize=16)
    
    steps = [1, 2, 3, 10]  # iters at each step
    titles = ['Initialize Centroids', 'Assign Points', 'Update Centroids', 'Final Clusters']
    
    for i, (ax, step, title) in enumerate(zip(axs.ravel(), steps, titles)):
        kmeans = KMeans(n_clusters=3, n_init=1, max_iter=step, random_state=42)
        kmeans.fit(X)
        ax.scatter(X[:, 0], X[:, 1], c=kmeans.labels_, cmap='viridis', alpha=0.7)
        ax.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], c='red', s=200, marker='X')
        ax.set_title(f'Step {i+1}: {title}')

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"


def generate_decision_tree_plot():
    # Generate sample data
    X, y = make_classification(n_samples=100, n_features=2, n_informative=2, n_redundant=0, n_classes=2, random_state=42)

    # Fit decision tree
    clf = DecisionTreeClassifier(max_depth=3, random_state=42)
    clf.fit(X, y)

    # Create plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot decision boundary
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                         np.arange(y_min, y_max, 0.1))
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    ax1.contourf(xx, yy, Z, alpha=0.4)
    ax1.scatter(X[:, 0], X[:, 1], c=y, alpha=0.8)
    ax1.set_title('Decision Tree Boundary')
    
    # Plot tree structure
    plot_tree(clf, filled=True, feature_names=['Feature 1', 'Feature 2'], class_names=['Class 0', 'Class 1'], ax=ax2)
    ax2.set_title('Decision Tree Structure')

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"


def generate_pca_plot():
    # Generate sample data
    X, _ = make_blobs(n_samples=200, centers=3, random_state=42)
    
    # Perform PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    # Create plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Original data
    ax1.scatter(X[:, 0], X[:, 1], alpha=0.7)
    ax1.set_title('Original Data')
    ax1.set_xlabel('Feature 1')
    ax1.set_ylabel('Feature 2')
    
    # PCA transformed data
    ax2.scatter(X_pca[:, 0], X_pca[:, 1], alpha=0.7)
    ax2.set_title('PCA Transformed Data')
    ax2.set_xlabel('First Principal Component')
    ax2.set_ylabel('Second Principal Component')

    for length, vector in zip(pca.explained_variance_, pca.components_):
        v = vector * 3 * np.sqrt(length)
        ax2.arrow(0, 0, v[0], v[1], head_width=0.1, head_length=0.1, linewidth=2, color='red')

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"

def generate_svm_plot():
    # Generate sample data
    np.random.seed(42)
    X, y = make_classification(n_samples=100, n_features=2, n_informative=2, n_redundant=0, n_classes=2, random_state=42)

    # Fit SVM
    svm = SVC(kernel='linear', C=1000)
    svm.fit(X, y)

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot decision boundary
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                         np.arange(y_min, y_max, 0.02))
    Z = svm.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    ax.contourf(xx, yy, Z, alpha=0.4)
    ax.scatter(X[:, 0], X[:, 1], c=y, alpha=0.8)
    
    # Plot support vectors
    ax.scatter(svm.support_vectors_[:, 0], svm.support_vectors_[:, 1], s=100, 
               linewidth=1, facecolors='none', edgecolors='k')
    
    ax.set_title('Support Vector Machine')
    ax.set_xlabel('Feature 1')
    ax.set_ylabel('Feature 2')

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"