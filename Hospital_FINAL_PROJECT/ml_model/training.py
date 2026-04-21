import pandas as pd
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import pickle
from pathlib import Path

# 1. Load dataset
script_dir = Path(__file__).resolve().parent
data_path = script_dir / "dataset" / "symptoms_dataset.csv"
df = pd.read_csv(data_path)

# 2. Features (X) and Target (y)
X = df.drop("disease", axis=1)
y = df["disease"]

# 3. Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

print(f"Dataset shape: {X.shape}")
print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
print("Train label distribution:\n", y_train.value_counts().to_string())
print("Test label distribution:\n", y_test.value_counts().to_string())

# Visualize train/test split
split_counts = [len(X_train), len(X_test)]
plt.figure(figsize=(6, 4))
plt.bar(["Train (80%)", "Test (20%)"], split_counts, color=["#4c72b0", "#55a868"])
plt.title("Training vs Testing Split")
plt.ylabel("Number of samples")
for i, value in enumerate(split_counts):
    plt.text(i, value + max(split_counts) * 0.01, str(value), ha="center", va="bottom")
plt.tight_layout()
plt.savefig("train_test_split.png")
plt.close()
print("✅ Saved split diagram: train_test_split.png")

# 4. Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Train and test accuracy

y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)
train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_test_pred)

print(f"✅ Training Accuracy: {train_accuracy * 100:.2f}%")
print(f"✅ Testing Accuracy: {test_accuracy * 100:.2f}%")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(
    RandomForestClassifier(n_estimators=100, random_state=42),
    X,
    y,
    cv=cv,
    scoring="accuracy",
)
print(
    f"✅ Cross-validation Accuracy: {cv_scores.mean() * 100:.2f}% "
    f"± {cv_scores.std() * 100:.2f}% (5 folds)"
)

# 6. Visualize accuracy
accuracy_values = [train_accuracy * 100, test_accuracy * 100]
plt.figure(figsize=(6, 4))
plt.bar(["Train", "Test"], accuracy_values, color=["#4c72b0", "#55a868"])
plt.ylim(0, 100)
plt.title("Model Accuracy")
plt.ylabel("Accuracy (%)")
for i, value in enumerate(accuracy_values):
    plt.text(i, value + 1, f"{value:.2f}%", ha="center", va="bottom")
plt.tight_layout()
plt.savefig("train_test_accuracy.png")
plt.close()
print("✅ Saved accuracy diagram: train_test_accuracy.png")

# 7. Save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model saved as model.pkl")