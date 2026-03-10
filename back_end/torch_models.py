import torch.nn as nn

class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.fc = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 10)  # salida: 10 clases
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.fc(x)
        return logits  # logits para CrossEntropyLoss
    
class CNN(nn.Module):
    def __init__(self):
        super().__init__()

        # --- Bloques convolucionales ---
        self.conv_block = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1),  # 28x28 -> 28x28
            nn.ReLU(),
            nn.MaxPool2d(2),  # 28x28 -> 14x14

            nn.Conv2d(32, 64, kernel_size=3, padding=1),  # 14x14 -> 14x14
            nn.ReLU(),
            nn.MaxPool2d(2),  # 14x14 -> 7x7

            nn.Conv2d(64, 128, kernel_size=3, padding=1),  # 7x7 -> 7x7
            nn.ReLU(),
            nn.MaxPool2d(2)  # 7x7 -> 3x3
        )

        # --- Flatten + Fully Connected ---
        self.flatten = nn.Flatten()
        self.fc = nn.Sequential(
            nn.Linear(128*3*3, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 10)  # logits para 10 clases
        )

    def forward(self, x):
        x = self.conv_block(x)
        x = self.flatten(x)
        logits = self.fc(x)
        return logits
    
name_to_model = {
    "MultiLayerPerceptron": MLP,
    "ConvolutionalNeuralNetwork": CNN
}