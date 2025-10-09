'use client'

import { useState } from 'react'
import { Calculator, TrendingUp, DollarSign, FileText, BarChart3, MapPin, Award } from 'lucide-react'

export default function Home() {
  const [zipcode, setZipcode] = useState('')
  const [prediction, setPrediction] = useState<any>(null)
  const [visualizations, setVisualizations] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handlePredict = async () => {
    setLoading(true)
    try {
      // Call Cloudflare Worker API for prediction
      const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/predict'
      
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ zipCode: zipcode }),
      })

      const data = await response.json()
      
      if (response.ok && !data.error) {
        // Transform API response to match expected format
        setPrediction({
          avgIncome: data.predictedIncome,
          confidence: Math.round(data.confidence * 100),
          percentile: Math.round((data.predictedIncome / 65000) * 100),
          nationalAvg: 65000,
          comparison: data.predictedIncome > 65000 ? 'above' : 'below'
        })

        // Fetch visualization data
        const vizResponse = await fetch('/api/visualize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ zipCode: zipcode }),
        })

        const vizData = await vizResponse.json()
        if (vizResponse.ok && vizData.success) {
          setVisualizations(vizData.visualizations)
        }
      } else {
        alert(data.error || 'Failed to get prediction. Try: 10001, 90001, 60601, 77001, 33109, 94027')
        setPrediction(null)
        setVisualizations(null)
      }
    } catch (error) {
      console.error('Prediction error:', error)
      alert('Failed to connect to prediction API')
      setPrediction(null)
      setVisualizations(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Header */}
      <header className="bg-irs-navy text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Calculator className="h-8 w-8" />
              <div>
                <h1 className="text-2xl font-bold">Regional Income Predictor</h1>
                <p className="text-blue-200 text-sm">Powered by IRS Tax Data & Machine Learning</p>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-6 text-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-tax-gold">95.0%</div>
                <div className="text-blue-200">Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-tax-gold">27.6K</div>
                <div className="text-blue-200">ZIP Codes</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-tax-gold">51</div>
                <div className="text-blue-200">States</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Predict Regional Income with AI
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Using real IRS tax statistics and advanced machine learning, 
            discover income predictions for any U.S. ZIP code with 94.5% accuracy
          </p>
        </div>

        {/* Main Prediction Card */}
        <div className="max-w-4xl mx-auto">
          <div className="tax-card bg-white border-2 border-tax-blue/20">
            <div className="border-b-2 border-gray-200 pb-4 mb-6">
              <h3 className="text-2xl font-bold text-tax-blue flex items-center">
                <FileText className="mr-2" />
                Income Prediction Calculator
              </h3>
              <p className="text-gray-600 mt-2">Enter a ZIP code to get instant income predictions</p>
            </div>

            {/* Input Form */}
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <MapPin className="inline mr-1 h-4 w-4" />
                  ZIP Code
                </label>
                <input
                  type="text"
                  value={zipcode}
                  onChange={(e) => setZipcode(e.target.value.replace(/\D/g, '').slice(0, 5))}
                  placeholder="Enter 5-digit ZIP code (e.g., 10001)"
                  className="tax-input w-full text-lg"
                  maxLength={5}
                />
              </div>

              <button
                onClick={handlePredict}
                disabled={zipcode.length !== 5 || loading}
                className="tax-button w-full text-lg flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                    <span>Analyzing Tax Data...</span>
                  </>
                ) : (
                  <>
                    <Calculator className="h-5 w-5" />
                    <span>Calculate Income Prediction</span>
                  </>
                )}
              </button>
            </div>

            {/* Results */}
            {prediction && (
              <div className="mt-8 pt-8 border-t-2 border-gray-200">
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Main Result */}
                  <div className="col-span-2 bg-gradient-to-r from-tax-blue to-blue-900 text-white rounded-xl p-6 shadow-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-blue-200 text-sm font-semibold uppercase">Predicted Average AGI</p>
                        <p className="text-5xl font-bold mt-2">
                          ${prediction.avgIncome.toLocaleString()}
                        </p>
                        <p className="text-blue-200 mt-2">
                          ZIP Code: <span className="font-mono font-bold">{zipcode}</span>
                        </p>
                      </div>
                      <DollarSign className="h-20 w-20 text-tax-gold opacity-50" />
                    </div>
                  </div>

                  {/* Confidence */}
                  <div className="bg-tax-green/10 border-2 border-tax-green rounded-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-gray-600 uppercase">Model Confidence</p>
                        <p className="text-4xl font-bold text-tax-green mt-2">{prediction.confidence}%</p>
                      </div>
                      <BarChart3 className="h-12 w-12 text-tax-green" />
                    </div>
                  </div>

                  {/* Percentile */}
                  <div className="bg-tax-gold/10 border-2 border-tax-gold rounded-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-gray-600 uppercase">National Percentile</p>
                        <p className="text-4xl font-bold text-tax-gold mt-2">{prediction.percentile}th</p>
                      </div>
                      <TrendingUp className="h-12 w-12 text-tax-gold" />
                    </div>
                  </div>

                  {/* Comparison */}
                  <div className="col-span-2 bg-gray-50 rounded-lg p-6 border-2 border-gray-200">
                    <h4 className="font-bold text-gray-900 mb-3">Comparison to National Average</h4>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600">National Average AGI:</p>
                        <p className="text-2xl font-bold text-gray-900">${prediction.nationalAvg.toLocaleString()}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-gray-600">This ZIP Code is:</p>
                        <p className="text-2xl font-bold text-tax-green">
                          {((prediction.avgIncome / prediction.nationalAvg - 1) * 100).toFixed(1)}% {prediction.comparison}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-900">
                    <strong>Note:</strong> This prediction is based on IRS SOI tax statistics and Census demographics. 
                    The Stacked Ensemble model was trained on 27,680 ZIP codes with 95.01% accuracy (R² = 0.9501).
                  </p>
                </div>
              </div>
            )}

            {/* Visualizations */}
            {visualizations && (
              <div className="mt-8 pt-8 border-t-2 border-gray-200 space-y-6">
                <h3 className="text-2xl font-bold text-gray-900 flex items-center">
                  <BarChart3 className="mr-2" />
                  Model Analysis & Insights
                </h3>

                {/* Model Comparison */}
                <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
                  <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                    <Award className="mr-2 h-5 w-5 text-tax-gold" />
                    Model Comparison - All 5 Models
                  </h4>
                  <div className="space-y-3">
                    {visualizations.modelComparison.labels.map((label: string, idx: number) => {
                      const prediction = visualizations.modelComparison.predictions[idx]
                      const accuracy = visualizations.modelComparison.accuracy[idx]
                      const maxPrediction = Math.max(...visualizations.modelComparison.predictions)
                      const barWidth = (prediction / maxPrediction) * 100
                      
                      return (
                        <div key={idx} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="font-medium text-gray-700">
                              {label} {idx === 0 && <span className="text-tax-gold">🏆</span>}
                            </span>
                            <span className="font-mono font-bold" style={{ color: visualizations.modelComparison.colors[idx] }}>
                              ${Math.round(prediction).toLocaleString()}
                            </span>
                          </div>
                          <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
                            <div 
                              className="absolute top-0 left-0 h-full transition-all duration-500 flex items-center justify-end px-3"
                              style={{ 
                                width: `${barWidth}%`,
                                backgroundColor: visualizations.modelComparison.colors[idx]
                              }}
                            >
                              <span className="text-white text-xs font-bold">
                                {accuracy.toFixed(2)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  <p className="text-xs text-gray-500 mt-4">
                    * Stacked Ensemble combines XGBoost, LightGBM, and Random Forest for superior accuracy
                  </p>
                </div>

                {/* Feature Importance */}
                <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
                  <h4 className="font-bold text-gray-900 mb-4">Feature Importance - What Drives This Prediction?</h4>
                  <div className="space-y-3">
                    {visualizations.featureImportance.labels.map((label: string, idx: number) => {
                      const value = visualizations.featureImportance.values[idx]
                      const barWidth = (value / Math.max(...visualizations.featureImportance.values)) * 100
                      
                      return (
                        <div key={idx} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="font-medium text-gray-700">{label}</span>
                            <span className="font-bold text-tax-blue">{(value * 100).toFixed(1)}%</span>
                          </div>
                          <div className="relative h-6 bg-gray-100 rounded-lg overflow-hidden">
                            <div 
                              className="absolute top-0 left-0 h-full transition-all duration-500"
                              style={{ 
                                width: `${barWidth}%`,
                                backgroundColor: visualizations.featureImportance.colors[idx]
                              }}
                            />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Regional Comparison */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
                    <h4 className="font-bold text-gray-900 mb-4">Regional Comparison</h4>
                    <div className="space-y-4">
                      {visualizations.regionalComparison.labels.map((label: string, idx: number) => {
                        const value = visualizations.regionalComparison.values[idx]
                        const isThisZip = idx === 0
                        
                        return (
                          <div key={idx} className={`flex justify-between items-center p-3 rounded-lg ${isThisZip ? 'bg-tax-green/10 border-2 border-tax-green' : 'bg-gray-50'}`}>
                            <span className={`font-medium ${isThisZip ? 'text-tax-green' : 'text-gray-700'}`}>
                              {label}
                            </span>
                            <span className={`text-lg font-bold ${isThisZip ? 'text-tax-green' : 'text-gray-900'}`}>
                              ${Math.round(value).toLocaleString()}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  </div>

                  <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
                    <h4 className="font-bold text-gray-900 mb-4">Demographics Overview</h4>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">Population</span>
                        <span className="text-lg font-bold text-gray-900">
                          {visualizations.demographics.population.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">Median Age</span>
                        <span className="text-lg font-bold text-gray-900">
                          {visualizations.demographics.medianAge} years
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">Education Rate</span>
                        <span className="text-lg font-bold text-tax-blue">
                          {visualizations.demographics.educationRate}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium text-gray-700">Unemployment</span>
                        <span className="text-lg font-bold text-tax-gold">
                          {visualizations.demographics.unemploymentRate}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-tax-blue/10 border-2 border-tax-blue rounded-lg">
                        <span className="font-medium text-tax-blue">Per Capita Income</span>
                        <span className="text-lg font-bold text-tax-blue">
                          ${visualizations.demographics.incomePerCapita.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Confidence Interval */}
                <div className="bg-gradient-to-r from-tax-green/10 to-tax-blue/10 border-2 border-tax-green rounded-lg p-6">
                  <h4 className="font-bold text-gray-900 mb-4">95% Confidence Interval</h4>
                  <div className="space-y-4">
                    <div className="relative h-16 bg-white rounded-lg overflow-hidden border-2 border-gray-200">
                      <div className="absolute inset-0 flex items-center justify-between px-4">
                        <div className="text-center">
                          <div className="text-xs text-gray-500">Lower Bound</div>
                          <div className="font-bold text-gray-700">
                            ${Math.round(visualizations.confidenceData.lower).toLocaleString()}
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="text-xs text-tax-green">Prediction</div>
                          <div className="font-bold text-tax-green text-xl">
                            ${Math.round(visualizations.confidenceData.prediction).toLocaleString()}
                          </div>
                        </div>
                        <div className="text-center">
                          <div className="text-xs text-gray-500">Upper Bound</div>
                          <div className="font-bold text-gray-700">
                            ${Math.round(visualizations.confidenceData.upper).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 text-center">
                      We are 95% confident the true average income falls within this range
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <div className="tax-card">
            <div className="bg-tax-blue/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <FileText className="h-6 w-6 text-tax-blue" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">IRS Tax Data</h3>
            <p className="text-gray-600">
              Real IRS SOI Individual Income Tax Statistics covering 27,680 ZIP codes across all 51 states
            </p>
          </div>

          <div className="tax-card">
            <div className="bg-tax-green/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <BarChart3 className="h-6 w-6 text-tax-green" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Stacked Ensemble ML</h3>
            <p className="text-gray-600">
              Research-based ensemble (XGBoost + LightGBM + RF) achieving 95.01% accuracy with RMSE of $10,451
            </p>
          </div>

          <div className="tax-card">
            <div className="bg-tax-gold/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <TrendingUp className="h-6 w-6 text-tax-gold" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Instant Predictions</h3>
            <p className="text-gray-600">
              Get immediate income predictions for any U.S. ZIP code with detailed analytics and insights
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-gray-400">
              Built with Python, Stacked Ensemble ML, Next.js, and deployed on Cloudflare Pages
            </p>
            <p className="text-gray-500 mt-2 text-sm">
              Data Source: IRS SOI Tax Statistics | Model Accuracy: 95.01% | © 2025
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
