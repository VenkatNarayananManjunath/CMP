import os
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import mlflow
import mlflow.pytorch
from mlflow.tracking import MlflowClient
import gc

# 1. Setup MLflow
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("CIFAR-10_Classification")

def train_cifar_model():
    # Hyperparameters
    params = {
        "lr": 0.001,
        "batch_size": 32,
        "epochs": 2,
        "architecture": "SimpleCNN"
    }

    # Data Transformation
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # Load CIFAR-10
    print("Downloading CIFAR-10 dataset...")
    trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=params["batch_size"], shuffle=True)

    # 2. Define Model
    class SimpleCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(3, 6, 5)
            self.pool = nn.MaxPool2d(2, 2)
            self.fc1 = nn.Linear(6 * 14 * 14, 10)

        def forward(self, x):
            x = self.pool(torch.relu(self.conv1(x)))
            x = torch.flatten(x, 1)
            x = self.fc1(x)
            return x

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = SimpleCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=params["lr"])

    # 3. Start MLflow Tracking
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        
        for epoch in range(params["epochs"]):
            running_loss = 0.0
            for i, data in enumerate(trainloader, 0):
                if i >= 5: # Extremely short for terminal output
                    break
                
                inputs, labels = data[0].to(device), data[1].to(device)
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()

            avg_loss = running_loss / 50
            print(f"Epoch {epoch+1} Loss: {avg_loss:.3f}")
            mlflow.log_metric("loss", avg_loss, step=epoch)

        # 4. Save and Register Model
        mlflow.pytorch.log_model(model, "cifar_model", registered_model_name="CIFAR10-Classifier")
        print(f"Model logged to MLflow and registered.")

if __name__ == "__main__":
    train_cifar_model()
