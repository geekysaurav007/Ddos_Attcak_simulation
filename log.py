import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Load the CSV file containing attack simulation data
data = pd.read_csv('attack_log.csv')

# Preprocess the data
# Convert 'server_status' from 'UP'/'DOWN' to binary (0 for 'UP', 1 for 'DOWN')
data['server_status'] = data['server_status'].apply(lambda x: 1 if x == 'DOWN' else 0)

# Feature selection: We'll use 'requests_sent', 'cpu_usage', 'memory_usage' as features
features = ['requests_sent', 'cpu_usage', 'memory_usage']
X = data[features]  # Features (request count, CPU usage, Memory usage)
y = data['server_status']  # Target (server status: UP or DOWN)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Initialize and train the Logistic Regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
print("Classification Report:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Plot the data and highlight when server status was DOWN
plt.figure(figsize=(12, 8))

# Plot Requests Sent over Time
plt.subplot(3, 1, 1)
plt.plot(data['timestamp'], data['requests_sent'], label='Requests Sent', color='blue')
plt.xlabel('Timestamp')
plt.ylabel('Requests Sent')
plt.title('Requests Sent Over Time')

# Highlight DOWN periods
down_times = data[data['server_status'] == 1]
plt.scatter(down_times['timestamp'], down_times['requests_sent'], color='red', label='Server DOWN')
plt.legend()

# Plot CPU Usage over Time
plt.subplot(3, 1, 2)
plt.plot(data['timestamp'], data['cpu_usage'], label='CPU Usage', color='orange')
plt.xlabel('Timestamp')
plt.ylabel('CPU Usage (%)')
plt.title('CPU Usage Over Time')

# Highlight DOWN periods
plt.scatter(down_times['timestamp'], down_times['cpu_usage'], color='red', label='Server DOWN')
plt.legend()

# Plot Memory Usage over Time
plt.subplot(3, 1, 3)
plt.plot(data['timestamp'], data['memory_usage'], label='Memory Usage', color='green')
plt.xlabel('Timestamp')
plt.ylabel('Memory Usage (%)')
plt.title('Memory Usage Over Time')

# Highlight DOWN periods
plt.scatter(down_times['timestamp'], down_times['memory_usage'], color='red', label='Server DOWN')
plt.legend()

# Show all plots
plt.tight_layout()
plt.show()

# Now the model and plots are ready
