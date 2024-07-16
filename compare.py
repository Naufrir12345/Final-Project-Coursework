import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

from FeatureExtraction import process_audio_folder #dipakai
from preproAudio import merekam #dipakai

# input_folder = "C:\\Users\\kurni\\Downloads\\oping\\VScodeFiles\\MainDataset\\datacoba"
# output_folder = "C:\\Users\\kurni\\Downloads\\oping\\VScodeFiles\\audio"

merekam() #dipakai

input_folder = "C:\\Users\\kurni\\Downloads\\oping\\coba-coba\\datasetRecap" #dipakai
output_folder = "C:\\Users\\kurni\\Downloads\\oping\\coba-coba\\datasetRecap" #dipakai

process_audio_folder(input_folder, output_folder, nfilt=40, frame_size=2800, hop_size=2400, num_ceps=13, ceps_liftering=12) #dipakai

# Setting up the plot style
sns.set_context('notebook')
plt.style.use('fivethirtyeight')
from warnings import filterwarnings
filterwarnings('ignore')

# Import data
df_book = pd.read_csv('C:\\Users\\kurni\\Downloads\oping\\coba-coba\\datasetRecap\\dataCoba.csv')
# df_sementara = pd.read_csv('C:\\Users\\kurni\\Downloads\\oping\\VScodeFiles\\afterLearning\\2section.csv')
# df_sementara = pd.read_csv('C:\\Users\\kurni\\Downloads\\oping\\VScodeFiles\\afterLearning\\3section.csv')
df_sementara = pd.read_csv('C:\\Users\\kurni\\Downloads\\oping\\VScodeFiles\\afterLearning\\4section.csv')
# df_sementara = pd.read_csv('C:\\Users\\kurni\\Downloads\\oping\\coba-coba\\mfcc_features.csv')

# df_book = pd.read_csv('C:\\Users\\kurni\\Downloads\\oping\\coba-coba\\datasetRecap\\dataGenerate\\new\\dataVompare.csv')
# df_sementara = pd.read_csv('C:\\Users\\kurni\\Downloads\\oping\\VScodeFiles\\afterLearning\\2section.csv')
# df_sementara = pd.read_csv('C:\\Users\\kurni\\Downloads\\oping\\coba-coba\\datasetRecap\\dataGenerate\\untukmatinyala\\datasetMatiNyala.csv')

# Combine data for training
df_combined = pd.concat([df_sementara, df_book], ignore_index=True)

# Select features for clustering
X = df_combined[['mfcc_1', 'mfcc_2', 'mfcc_3', 'mfcc_4']]

# Handle NaN values using SimpleImputer
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# Standardize the data
scaler = StandardScaler()
X_std = scaler.fit_transform(X_imputed)

# Perform PCA for dimensionality reduction
# pca = PCA(n_components=2)
# pca = PCA(n_components=3)
pca = PCA(n_components=4)
X_pca = pca.fit_transform(X_std)

# Run K-Means on PCA-transformed data
# kmeans = KMeans(n_clusters=2, max_iter=800, random_state=42)
# kmeans = KMeans(n_clusters=3, max_iter=800, random_state=42)
kmeans = KMeans(n_clusters=4, max_iter=800, random_state=42)
kmeans.fit(X_pca)
labels_kmeans = kmeans.labels_
centroids_kmeans = kmeans.cluster_centers_

# Compute silhouette score for K-Means
silhouette_avg_kmeans = silhouette_score(X_std, labels_kmeans)
print(f"Silhouette Score (K-Means): {silhouette_avg_kmeans}")

# Run DBSCAN on PCA-transformed data
dbscan = DBSCAN(eps=0.5, min_samples=5)
labels_dbscan = dbscan.fit_predict(X_pca)

# Map cluster labels to 'NAIK' and 'TURUN'
def map_kmeans_labels(label):
    if label == 0:
        return "TURUN"
    elif label == 1:
        return "NYALAKAN"
    elif label == 2:
        return "NAIK"
    elif label == 3:
        return "MATIKAN"

    else:
        return "Unknown"

def map_dbscan_labels(label):
    if label == 0:
        return "TURUN"
    elif label == 1:
        return "NYALAKAN"
    elif label == 2:
        return "NAIK"
    elif label == 3:
        return "MATIKAN"

    else:
        return "Unknown"

# Plot the clustered data for K-Means
fig, ax = plt.subplots(figsize=(8, 6))
unique_labels = np.unique(labels_kmeans)
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

# Plot each cluster
for k, col in zip(unique_labels, colors):
    class_member_mask = (labels_kmeans == k)
    xy = X_pca[class_member_mask]
    
    # Plot points
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)
    
    # Display cluster label
    label = map_kmeans_labels(k)
    plt.text(np.mean(xy[:, 0]), np.mean(xy[:, 1]), label, color='black', fontsize=12, ha='center', va='center')

# Plot centroids
# plt.scatter(centroids_kmeans[:, 0], centroids_kmeans[:, 1], marker='*', s=300, c=['blue', 'green'], label='centroid')
# plt.scatter(centroids_kmeans[:, 0], centroids_kmeans[:, 1], marker='*', s=300, c=['blue', 'green','yellow'], label='centroid')
plt.scatter(centroids_kmeans[:, 0], centroids_kmeans[:, 1], marker='*', s=300, c=['blue', 'green','yellow','red'], label='centroid')

# Add labels for centroids
for i, centroid in enumerate(centroids_kmeans):
    plt.text(centroid[0], centroid[1], f'Centroid {i}', color='black', fontsize=12, ha='center', va='center')

plt.title('Clustered Data (PCA) - K-Means')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.legend()

# Set equal scaling for axis
plt.axis('equal')

plt.show()

# Plot the clustered data for DBSCAN
fig, ax = plt.subplots(figsize=(8, 6))
unique_labels = np.unique(labels_dbscan)
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

for k, col in zip(unique_labels, colors):
    if k == -1:
        col = [0, 0, 0, 1]

    class_member_mask = (labels_dbscan == k)
    xy = X_pca[class_member_mask]
    
    # Display the label of each data point
    for i, idx in enumerate(df_combined.index[class_member_mask]):
        plt.text(xy[i, 0], xy[i, 1], str(idx), color='black', fontsize=8, ha='center', va='center')
    
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)

plt.title('Clustered Data (PCA) - DBSCAN')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')

# Set equal scaling for axis
plt.axis('equal')

plt.show()

# Predict clusters for new data (Book.csv)
new_data_subset = df_book[['mfcc_1', 'mfcc_2', 'mfcc_3', 'mfcc_4']]

# Handle NaN values using SimpleImputer
new_data_imputed = imputer.transform(new_data_subset)

# Standardize the new data
new_data_std = scaler.transform(new_data_imputed)

# Transform new data using PCA
new_data_pca = pca.transform(new_data_std)

# Predict clusters for the new data using K-Means
predicted_clusters_kmeans = kmeans.predict(new_data_pca)

# Predict clusters for the new data using DBSCAN
predicted_clusters_dbscan = dbscan.fit_predict(new_data_pca)

predicted_labels_kmeans = list(map(map_kmeans_labels, predicted_clusters_kmeans))
predicted_labels_dbscan = list(map(map_dbscan_labels, predicted_clusters_dbscan))

# Print predicted clusters
print("Predicted clusters for new data (K-Means):")
print(predicted_labels_kmeans)

print("Predicted clusters for new data (DBSCAN):")
print(predicted_labels_dbscan)

# Save predicted labels to files
with open('predicted_labels_kmeans.txt', 'w') as file:
    for label in predicted_labels_kmeans:
        file.write(f"{label}\n")

with open('predicted_labels_dbscan.txt', 'w') as file:
    for label in predicted_labels_dbscan:
        file.write(f"{label}\n")

# Plot the data from 'Book.csv' with predicted clusters for K-Means
plt.figure(figsize=(8, 6))
plt.scatter(new_data_pca[:, 0], new_data_pca[:, 1], c=predicted_clusters_kmeans, cmap='viridis', marker='X')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.title('Data from Book.csv with Predicted Clusters (K-Means)')
plt.colorbar(label='Predicted Cluster')

# Set equal scaling for axis
plt.axis('equal')

# Add lines connecting new data points to the nearest centroids
for i in range(len(new_data_pca)):
    nearest_centroid_index = np.argmin(np.linalg.norm(centroids_kmeans - new_data_pca[i], axis=1))
    centroid = centroids_kmeans[nearest_centroid_index]
    plt.plot([centroid[0], new_data_pca[i, 0]], [centroid[1], new_data_pca[i, 1]], linestyle='--', color='black')
    label = map_kmeans_labels(nearest_centroid_index)
    plt.text(new_data_pca[i, 0], new_data_pca[i, 1], label, color='red', fontsize=12, ha='center', va='center')

plt.show()

# Plot the data from 'Book.csv' with predicted clusters for DBSCAN
plt.figure(figsize=(8, 6))
plt.scatter(new_data_pca[:, 0], new_data_pca[:, 1], c=predicted_clusters_dbscan, cmap='viridis', marker='X')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.title('Data from Book.csv with Predicted Clusters (DBSCAN)')
plt.colorbar(label='Predicted Cluster')

# Set equal scaling for axis
plt.axis('equal')

plt.show()

# Plot the final combined plot
fig, ax = plt.subplots(figsize=(8, 6))
for k, col in zip(unique_labels, colors):
    class_member_mask = (labels_kmeans == k)
    xy = X_pca[class_member_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=6)
plt.scatter(centroids_kmeans[:, 0], centroids_kmeans[:, 1], marker='*', s=300, c='r', label='centroid')

# Calculate the radius for circles around centroids
radius_kmeans = []
for i, centroid in enumerate(centroids_kmeans):
    max_distance = np.max(np.linalg.norm(X_pca[labels_kmeans == i] - centroid, axis=1))
    radius_kmeans.append(max_distance)

# Plot the circles around centroids
for radius, centroid in zip(radius_kmeans, centroids_kmeans):
    circle = plt.Circle(centroid, radius, color='r', fill=False, linestyle='--')
    ax.add_artist(circle)

# Add lines connecting new data points to the nearest centroids
for i in range(len(new_data_pca)):
    nearest_centroid_index = np.argmin(np.linalg.norm(centroids_kmeans - new_data_pca[i], axis=1))
    centroid = centroids_kmeans[nearest_centroid_index]
    plt.plot([centroid[0], new_data_pca[i, 0]], [centroid[1], new_data_pca[i, 1]], linestyle='--', color='yellow')

plt.scatter(new_data_pca[:, 0], new_data_pca[:, 1], c=predicted_clusters_kmeans, cmap='viridis', marker='X', label='New Data Points')
plt.title('Clustered Data (PCA) - K-Means with New Data Points')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.legend()
plt.show()
