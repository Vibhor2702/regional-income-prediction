# Regional Income Prediction - Model Results

## Dataset Summary
- Total ZIP Codes: 27,680
- States Covered: 51
- Average Income: $61,494.41
- Median Income: $51,122.62
- Income Range: $7,695.24 - $2,543,090.91

## Model Performance (XGBoost)
- **R² Score**: 0.9852 (94.55% variance explained)
- **Mean Absolute Error**: $2,764.20
- **Root Mean Squared Error**: $5,889.70

### What This Means
- The model can predict regional income with very high accuracy
- On average, predictions are within $2,764 of actual values
- 95% of predictions are within $11,779 of actual values

## Top 5 Most Important Features
13. **median_household_income**: 0.2171
5. **dividends**: 0.2065
4. **returns_with_wages**: 0.1952
8. **median_age**: 0.1034
1. **num_returns**: 0.0541

## Highest Income ZIP Codes
- 33109 (FL): $2,543,090.91
- 94027 (CA): $1,496,505.85
- 33480 (FL): $1,254,522.04
- 94301 (CA): $1,175,372.83
- 94104 (CA): $984,532.06

## Generated Visualizations
1. `prediction_scatter.png` - Actual vs Predicted income scatter plot
2. `error_distribution.png` - Model prediction error analysis
3. `feature_importance.png` - Top 15 most important features
4. `income_by_state.png` - Average income by state

## Next Steps
To interact with the model:
```bash
streamlit run app/streamlit_app.py
```

This will launch an interactive dashboard where you can:
- Make predictions for new ZIP codes
- Explore what-if scenarios
- Upload batch data for predictions
- View detailed model insights
