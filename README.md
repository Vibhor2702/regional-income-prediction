# 🏘️ Regional Income Prediction

**A comprehensive income prediction sy## 📊 Model Performance

| Model | Accuracy (R²) | RMSE | MAE | Speed | Explainability |
|-------|--------------|------|-----|-------|----------------|
| **Traditional Statistical** | ~87-90% | ~$12K | ~$4.5K | <10ms | ⭐⭐⭐⭐⭐ |
| **Pure ML (Stacked)** | **95.01%** | $10,451 | $3,686 | ~120ms | ⭐⭐⭐ |
| **Hybrid (Weighted)** | ~93-94% | ~$11K | ~$4K | ~130ms | ⭐⭐⭐⭐ |

**Training Data**: 27,680 ZIP codes | **Research Foundation**: 188+ papers analyzedth 3 distinct prediction methods: Traditional Statistical, Pure ML, and Hybrid - achieving 95.01% accuracy with full explainability.**

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Deployed](https://img.shields.io/badge/deployed-cloudflare-orange.svg)
![Accuracy](https://img.shields.io/badge/accuracy-95.01%25-brightgreen.svg)

## 🚀 Live Demo

**Web App**: https://regional-income-prediction.pages.dev

**Try these ZIP codes**: 10001 (NYC), 90001 (LA), 60601 (Chicago), 77001 (Houston), 33109 (Miami), 94027 (Atherton)

---

## ⭐ Key Features

### 🎯 Three Prediction Methods

1. **Traditional Statistical Model** 📊
   - Econometric formulas based on 188+ research papers
   - 100% deterministic (no randomness)
   - Fully explainable with component breakdown
   - Based on Jenkins (2000), Ibragimov (2009), Chung (2022)
   - **Formula**: `Base Income × COL × (1 + Education) × (1 - Unemployment) × Demographics × GDP`

2. **Pure ML Model (Stacked Ensemble)** 🤖
   - XGBoost + LightGBM + Random Forest + Ridge meta-learner
   - **95.01% accuracy** (R² = 0.9501)
   - RMSE: $10,451 | MAE: $3,686
   - Research-enhanced (Verme 2025, Zhou & Wen 2024)

3. **Hybrid Model (Weighted Ensemble)** 🔄
   - **60% ML + 40% Traditional** weighted combination
   - Best of both worlds: accuracy + explainability
   - Confidence penalty if predictions disagree >20%
   - Intelligent recommendation engine

### � Method Comparison Feature

- **Compare All 3 Methods** side-by-side
- Agreement analysis (high/medium/low)
- Variance and standard deviation statistics
- Intelligent recommendation based on context
- 3 comparison visualizations

---

## 🎯 Project Overview

End-to-end machine learning pipeline with modern web interface and 3 distinct prediction methodologies:

- **Dataset**: 27,680 ZIP codes from IRS SOI Tax Statistics (2015)
- **Features**: 22 engineered features (tax data, demographics, economics)
- **Web Stack**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: Cloudflare Pages Functions (serverless)
- **Deployment**: Global edge network with automatic HTTPS

## 🛠️ Technology Stack

### Machine Learning
- **Python 3.11**, pandas, numpy
- **XGBoost** & **LightGBM** for ensemble models
- **scikit-learn** for preprocessing and evaluation

### Web Application
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend**: Cloudflare Pages Functions (serverless)
- **Icons**: Lucide React
- **Deployment**: Cloudflare Pages with automatic HTTPS

## � Model Performance

- **Algorithm**: XGBoost Regressor
- **Accuracy**: 94.5% (R² = 0.9455)
- **MAE**: $3,591
- **RMSE**: $6,034
- **Dataset**: 27,680 ZIP codes

## 🎯 Available Test ZIP Codes

- `10001` - New York, NY ($85K median)
- `90001` - Los Angeles, CA ($45K median)
- `60601` - Chicago, IL ($70K median)
- `77001` - Houston, TX ($62K median)
- `33109` - Miami Beach, FL ($95K median)
- `94027` - Atherton, CA ($150K median)

## 🚀 Local Development

### ML Pipeline
```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python src/data_preprocessing.py
python src/feature_engineering.py
python src/model_training.py
python src/model_evaluation.py
```

### Web Application
```bash
cd web
npm install --legacy-peer-deps
npm run dev           # Development server
npm run build         # Production build
```

## 🎨 API Endpoints

### 1. Traditional Statistical Prediction
```bash
curl -X POST https://regional-income-prediction.pages.dev/api/predict-traditional \
  -H "Content-Type: application/json" \
  -d '{"zipCode": "10001"}'
```

### 2. Pure ML Prediction
```bash
curl -X POST https://regional-income-prediction.pages.dev/api/predict-ml \
  -H "Content-Type: application/json" \
  -d '{"zipCode": "10001"}'
```

### 3. Hybrid Prediction
```bash
curl -X POST https://regional-income-prediction.pages.dev/api/predict-hybrid \
  -H "Content-Type: application/json" \
  -d '{"zipCode": "10001"}'
```

### 4. Compare All Methods
```bash
curl -X POST https://regional-income-prediction.pages.dev/api/compare-methods \
  -H "Content-Type: application/json" \
  -d '{"zipCode": "10001"}'
```

### Response Example
```json
{
  "zipCode": "10001",
  "state": "NY",
  "predictedIncome": 87234,
  "confidence": 0.92,
  "medianIncome": 85000,
  "population": 21000,
  "metadata": {
    "model": "XGBoost",
    "version": "1.0.0"
  }
}
```

## 📁 Project Structure

```
regional-income-prediction/
├── src/                          # ML pipeline
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   └── model_evaluation.py
├── web/                          # Next.js frontend
│   ├── app/                      # App router pages
│   ├── functions/                # API endpoints
│   │   └── api/
│   │       ├── predict.ts        # Prediction endpoint
│   │       └── health.ts         # Health check
│   └── package.json
├── models/                       # Trained models (not in git)
├── reports/                      # Visualization charts
└── README.md
```

## 🔄 Deployment

Automatically deployed to Cloudflare Pages on every push to main:

```bash
cd web
npm run build
npx wrangler pages deploy out --project-name regional-income-prediction
```

## � License

MIT License

## 👤 Author

**Vibhor** - [GitHub](https://github.com/Vibhor2702)

---

**Built with ❤️ using XGBoost, Next.js, and Cloudflare**
