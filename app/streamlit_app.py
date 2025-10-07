"""
Streamlit Dashboard for Regional Income Prediction.

This interactive web application provides:
1. Manual data input form for single predictions
2. CSV upload for batch predictions
3. Interactive choropleth map of predictions vs actuals
4. What-if analysis with sliders
5. Feature importance visualization
6. Model performance metrics

Usage:
    streamlit run app/streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import MODELS_DIR, REPORTS_DIR, BEST_MODEL_FILE, FEATURE_PIPELINE_FILE
from src.helpers import load_model
from src.logger import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Regional Income Prediction",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_models():
    """Load trained model and preprocessing pipeline."""
    try:
        model = load_model(MODELS_DIR / BEST_MODEL_FILE)
        pipeline = load_model(MODELS_DIR / FEATURE_PIPELINE_FILE)
        return model, pipeline
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None


@st.cache_data
def load_results():
    """Load model evaluation results."""
    try:
        results_path = REPORTS_DIR / "model_results.json"
        with open(results_path, 'r') as f:
            results = json.load(f)
        return results
    except Exception as e:
        st.warning(f"Could not load results: {e}")
        return {}


def create_input_form():
    """Create manual input form for single prediction."""
    st.subheader("📝 Enter Region Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        median_household_income = st.number_input(
            "Median Household Income ($)",
            min_value=10000,
            max_value=250000,
            value=65000,
            step=1000
        )
        
        per_capita_income = st.number_input(
            "Per Capita Income ($)",
            min_value=10000,
            max_value=150000,
            value=35000,
            step=1000
        )
        
        total_population = st.number_input(
            "Total Population",
            min_value=100,
            max_value=10000000,
            value=50000,
            step=1000
        )
        
        total_households = st.number_input(
            "Total Households",
            min_value=50,
            max_value=5000000,
            value=20000,
            step=500
        )
    
    with col2:
        unemployment_rate = st.slider(
            "Unemployment Rate (%)",
            min_value=0.0,
            max_value=30.0,
            value=5.0,
            step=0.5
        ) / 100
        
        poverty_rate = st.slider(
            "Poverty Rate (%)",
            min_value=0.0,
            max_value=50.0,
            value=12.0,
            step=1.0
        ) / 100
        
        education_rate = st.slider(
            "College Education Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=30.0,
            step=1.0
        ) / 100
        
        median_age = st.slider(
            "Median Age",
            min_value=20.0,
            max_value=70.0,
            value=38.0,
            step=1.0
        )
    
    with col3:
        median_home_value = st.number_input(
            "Median Home Value ($)",
            min_value=50000,
            max_value=2000000,
            value=250000,
            step=10000
        )
        
        median_gross_rent = st.number_input(
            "Median Gross Rent ($)",
            min_value=300,
            max_value=5000,
            value=1200,
            step=50
        )
        
        avg_household_size = st.number_input(
            "Average Household Size",
            min_value=1.0,
            max_value=10.0,
            value=2.5,
            step=0.1
        )
        
        owner_occupied_rate = st.slider(
            "Owner-Occupied Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=65.0,
            step=1.0
        ) / 100
    
    # Create feature dictionary
    features = {
        'median_household_income': median_household_income,
        'per_capita_income': per_capita_income,
        'total_population': total_population,
        'total_households': total_households,
        'avg_household_size': avg_household_size,
        'median_age': median_age,
        'unemployment_rate': unemployment_rate,
        'poverty_rate': poverty_rate,
        'education_rate': education_rate,
        'median_home_value': median_home_value,
        'median_gross_rent': median_gross_rent,
        'owner_occupied_rate': owner_occupied_rate,
    }
    
    return features


def make_prediction(model, features_dict):
    """Make prediction from feature dictionary."""
    # Convert to DataFrame
    df = pd.DataFrame([features_dict])
    
    # Fill missing columns with defaults
    expected_features = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else []
    for feat in expected_features:
        if feat not in df.columns:
            df[feat] = 0
    
    # Ensure correct column order
    if expected_features:
        df = df[expected_features]
    
    # Make prediction
    prediction = model.predict(df)[0]
    
    return prediction


def create_what_if_analysis(model, base_features):
    """Create what-if analysis with interactive sliders."""
    st.subheader("🔀 What-If Analysis")
    st.write("Adjust variables below to see how predictions change:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        income_multiplier = st.slider(
            "Median Income Multiplier",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        education_change = st.slider(
            "Education Rate Change (percentage points)",
            min_value=-20.0,
            max_value=20.0,
            value=0.0,
            step=1.0
        ) / 100
    
    with col2:
        unemployment_change = st.slider(
            "Unemployment Rate Change (percentage points)",
            min_value=-10.0,
            max_value=10.0,
            value=0.0,
            step=0.5
        ) / 100
        
        home_value_multiplier = st.slider(
            "Home Value Multiplier",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
    
    # Apply changes
    modified_features = base_features.copy()
    modified_features['median_household_income'] *= income_multiplier
    modified_features['per_capita_income'] *= income_multiplier
    modified_features['education_rate'] = min(1.0, max(0.0, 
        modified_features['education_rate'] + education_change))
    modified_features['unemployment_rate'] = min(1.0, max(0.0,
        modified_features['unemployment_rate'] + unemployment_change))
    modified_features['median_home_value'] *= home_value_multiplier
    
    # Make predictions
    base_prediction = make_prediction(model, base_features)
    modified_prediction = make_prediction(model, modified_features)
    
    # Display results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Base Prediction", f"${base_prediction:,.0f}")
    
    with col2:
        st.metric("Modified Prediction", f"${modified_prediction:,.0f}")
    
    with col3:
        change = modified_prediction - base_prediction
        change_pct = (change / base_prediction) * 100
        st.metric(
            "Change",
            f"${change:,.0f}",
            f"{change_pct:+.1f}%"
        )


def create_feature_importance_plot(results_path=None):
    """Create feature importance visualization."""
    st.subheader("📊 Feature Importance")
    
    try:
        # Try to load SHAP or permutation importance
        importance_path = REPORTS_DIR / "feature_importance" / "permutation_importance.csv"
        
        if importance_path.exists():
            importance_df = pd.read_csv(importance_path).head(15)
            
            fig = go.Figure(go.Bar(
                x=importance_df['importance_mean'],
                y=importance_df['feature'],
                orientation='h',
                error_x=dict(type='data', array=importance_df['importance_std']),
                marker=dict(color='steelblue')
            ))
            
            fig.update_layout(
                title="Top 15 Features by Permutation Importance",
                xaxis_title="Importance Score",
                yaxis_title="Feature",
                height=500,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Feature importance data not available. Run `python src/interpret.py` first.")
    
    except Exception as e:
        st.error(f"Error loading feature importance: {e}")


def create_map_visualization():
    """Create choropleth map of predictions."""
    st.subheader("🗺️ Geographic Visualization")
    st.info("Map visualization requires geographic data. This is a placeholder for when shapefiles are loaded.")
    
    # Placeholder map centered on US
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=39.8283,
            longitude=-98.5795,
            zoom=3,
            pitch=0,
        ),
    ))


def upload_and_predict(model):
    """Handle CSV upload and batch predictions."""
    st.subheader("📤 Batch Predictions")
    
    uploaded_file = st.file_uploader("Upload CSV file with region data", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write(f"Loaded {len(df)} records")
            
            # Display first few rows
            st.write("Preview:")
            st.dataframe(df.head())
            
            if st.button("Generate Predictions"):
                with st.spinner("Making predictions..."):
                    # Ensure required columns exist
                    required_cols = ['median_household_income', 'per_capita_income', 
                                   'total_population', 'total_households']
                    
                    missing_cols = set(required_cols) - set(df.columns)
                    if missing_cols:
                        st.error(f"Missing required columns: {missing_cols}")
                        return
                    
                    # Make predictions
                    try:
                        predictions = model.predict(df)
                        df['predicted_agi'] = predictions
                        
                        st.success("✓ Predictions complete!")
                        st.dataframe(df)
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download predictions as CSV",
                            data=csv,
                            file_name="predictions.csv",
                            mime="text/csv"
                        )
                    except Exception as e:
                        st.error(f"Prediction error: {e}")
        
        except Exception as e:
            st.error(f"Error loading file: {e}")


def display_model_metrics(results):
    """Display model performance metrics."""
    st.subheader("📈 Model Performance")
    
    if not results:
        st.info("No model results available. Run `python src/modeling.py` first.")
        return
    
    # Create comparison dataframe
    metrics_df = pd.DataFrame(results).T
    metrics_df = metrics_df.sort_values('RMSE')
    
    # Display as table
    st.dataframe(
        metrics_df.style.format({
            'MAE': '{:,.2f}',
            'RMSE': '{:,.2f}',
            'R2': '{:.4f}',
            'MAPE': '{:.2f}%'
        }).highlight_min(subset=['RMSE', 'MAE', 'MAPE'], color='lightgreen')
        .highlight_max(subset=['R2'], color='lightgreen'),
        use_container_width=True
    )
    
    # Best model highlight
    best_model = metrics_df.index[0]
    st.success(f"🏆 Best Model: **{best_model}** (RMSE: ${metrics_df.loc[best_model, 'RMSE']:,.2f})")


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">💰 Regional Income Prediction Dashboard</h1>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Load models
    with st.spinner("Loading models..."):
        model, pipeline = load_models()
        results = load_results()
    
    if model is None:
        st.error("⚠️ Models not found. Please run the training pipeline first:")
        st.code("make prepare  # Download data\nmake train    # Train models")
        return
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/us-dollar-circled--v1.png", width=100)
        st.title("Navigation")
        
        page = st.radio(
            "Select Page:",
            ["🏠 Home", "🔮 Single Prediction", "📊 Batch Predictions", 
             "📈 Model Performance", "🗺️ Geographic View"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info(
            "This dashboard predicts average Adjusted Gross Income (AGI) "
            "for U.S. regions using IRS tax data and Census socio-economic indicators."
        )
        
        st.markdown("---")
        st.markdown("### Data Sources")
        st.markdown("- **IRS SOI** Tax Statistics")
        st.markdown("- **U.S. Census** ACS 5-year")
        st.markdown("- **HUD** ZIP-County Crosswalk")
    
    # Main content
    if page == "🏠 Home":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("### 🎯 Prediction\nMake single or batch predictions for regional income")
        
        with col2:
            st.success("### 📊 Analysis\nExplore feature importance and what-if scenarios")
        
        with col3:
            st.warning("### 🗺️ Visualization\nView geographic distribution of predictions")
        
        st.markdown("---")
        display_model_metrics(results)
        
        st.markdown("---")
        create_feature_importance_plot()
    
    elif page == "🔮 Single Prediction":
        features = create_input_form()
        
        if st.button("🔮 Predict Average AGI", type="primary"):
            with st.spinner("Making prediction..."):
                prediction = make_prediction(model, features)
                
                st.success(f"### Predicted Average AGI: ${prediction:,.0f}")
                
                st.balloons()
        
        st.markdown("---")
        create_what_if_analysis(model, features)
    
    elif page == "📊 Batch Predictions":
        upload_and_predict(model)
    
    elif page == "📈 Model Performance":
        display_model_metrics(results)
        
        st.markdown("---")
        create_feature_importance_plot()
    
    elif page == "🗺️ Geographic View":
        create_map_visualization()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Regional Income Prediction System | Built with Streamlit | 2025"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
