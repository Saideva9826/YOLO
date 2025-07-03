import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv("retail_sales_data.csv")
data["Date"] = pd.to_datetime(data["Date"])
data.set_index("Date", inplace=True)

# Split data into training and testing sets
train_data = data[:-12] # Use all but last 12 months for training
test_data = data[-12:]  # Use last 12 months for testing

# Fit ARIMA model
# (p,d,q) parameters: p=AR order, d=differencing order, q=MA order
# These parameters would typically be determined through ACF/PACF plots or auto_arima
# For this example, we'll use a common set of parameters (1,1,1)
model = ARIMA(train_data["Sales"], order=(1,1,1))
model_fit = model.fit()

# Make predictions
start_index = len(train_data)
end_index = len(data) - 1
predictions = model_fit.predict(start=start_index, end=end_index, typ=\

