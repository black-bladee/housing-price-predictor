# 🏠 California Housing Price Predictor

A Machine Learning application that predicts **California housing prices** using a **Random Forest Regression model** with an interactive **Tkinter desktop UI**.

This project combines **data preprocessing, model training, and a professional GUI interface** to allow users to estimate property values based on multiple housing features.

---

## 🚀 Features

* 📊 **Random Forest Regression Model**
* ⚙️ **Scikit-Learn Pipeline for Data Preprocessing**
* 🖥️ **Interactive Tkinter Desktop UI**
* 📍 Location-based housing price estimation
* 📈 Model confidence indicator
* 📉 Additional analytics:

  * Price per room
  * Income ratio
  * Population density
  * Rooms per household
  * Prediction price band

---

## 🧠 Machine Learning Model

The model is trained on the **California Housing Dataset** using:

* **RandomForestRegressor**
* **Stratified Sampling**
* **Data Preprocessing Pipeline**

### Preprocessing Pipeline

* Missing value handling with **SimpleImputer**
* Feature scaling using **StandardScaler**
* Categorical encoding using **OneHotEncoder**

---

## 🏗️ Project Structure

```
housing-price-predictor
│
├── housing_estimator.py      # Tkinter GUI application
├── main.py                   # Model training script
├── housing.csv               # Dataset
├── input.csv                 # Test input dataset
├── output.csv                # Model prediction output
├── pipeline.pkl              # Saved preprocessing pipeline
├── model.pkl                 # Trained Random Forest model
└── README.md
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/housing-price-predictor.git
cd housing-price-predictor
```

Install dependencies:

```bash
pip install pandas numpy scikit-learn joblib
```

---

## ▶️ Running the Project

### 1️⃣ Train the Model

```bash
python main.py
```

This generates:

```
model.pkl
pipeline.pkl
```

---

### 2️⃣ Run the GUI Application

```bash
python housing_estimator.py
```

The application will launch a **desktop interface** where users can enter housing details and estimate property values.

---

## 🖥️ Application Interface

The GUI allows users to input:

* Latitude
* Longitude
* Housing Median Age
* Total Rooms
* Total Bedrooms
* Population
* Number of Households
* Median Income
* Ocean Proximity

The model then predicts the **median house value** along with additional analytics.

---

## 🧪 Simulation Mode

The UI includes a **simulation mode** for quick demos without loading the trained model.

To use the real model:

```python
USE_REAL_MODEL = True
```

Make sure `model.pkl` and `pipeline.pkl` exist in the project directory.

---

## 📊 Technologies Used

* **Python**
* **Scikit-Learn**
* **Pandas**
* **NumPy**
* **Tkinter**
* **Joblib**

---

## 🎯 Learning Outcomes

This project demonstrates:

* Machine Learning model training
* Data preprocessing pipelines
* Feature engineering
* Model deployment in a GUI application
* Interactive data visualization in Python

---

## 📌 Future Improvements

* Map-based location selection
* Feature importance visualization
* Model comparison dashboard
* Web application version (Flask / FastAPI)
* Deployment using Docker

---

## 👨‍💻 Author

**Pranav Kulthe**

If you found this project helpful, feel free to ⭐ the repository.
