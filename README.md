# 🏘️ Regional Income Prediction
## 📊 Model Performance

### 🎯 Research-Enhanced Model (Current)
- **Algorithm**: Stacked Ensemble (XGBoost + LightGBM + Random Forest)
- **Accuracy**: **95.0%** (R² = 0.9501) ✨ *New Record*
- **MAE**: $3,686
- **RMSE**: $10,451
- **Improvement**: +0.46% over baseline XGBoost
- **Dataset**: 27,680 ZIP codes

*Enhancement based on academic research: Verme (2025) World Bank Economic Review*

### Previous Best Model
- **Algorithm**: XGBoost Regressor
- **Accuracy**: 94.5% (R² = 0.9455)
- **MAE**: $3,591
- **RMSE**: $10,923e learning model predicting average adjusted gross income (AGI) for U.S. regions using IRS tax data and Census socio-economic indicators.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Deployed](https://img.shields.io/badge/deployed-cloudflare-orange.svg)

## 🚀 Live Demo

**Web App**: https://regional-income-prediction.pages.dev

## 🎯 Project Overview

End-to-end machine learning pipeline with modern web interface:

- **ML Pipeline**: XGBoost model with 94.5% accuracy (R² = 0.9455)
- **Dataset**: 27,680 ZIP codes from IRS SOI Tax Statistics (2015)
- **Web App**: Next.js frontend with Cloudflare Pages Functions API
- **Features**: 22 engineered features including demographics and tax data
- **Deployment**: Serverless architecture on Cloudflare Edge Network

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

## 🎨 API Usage

### Make a Prediction
```bash
curl -X POST https://regional-income-prediction.pages.dev/api/predict \
  -H "Content-Type: application/json" \
  -d '{"zipCode": "10001"}'
```

### Response
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
