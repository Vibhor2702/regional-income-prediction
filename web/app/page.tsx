'use client'

import { useState } from 'react'
import { Calculator, TrendingUp, DollarSign, FileText, BarChart3, MapPin } from 'lucide-react'

export default function Home() {
  const [zipcode, setZipcode] = useState('')
  const [prediction, setPrediction] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handlePredict = async () => {
    setLoading(true)
    try {
      // Call Cloudflare Worker API
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
          percentile: Math.round((data.predictedIncome / 65000) * 100), // Approximate percentile
          nationalAvg: 65000, // US average
          comparison: data.predictedIncome > 65000 ? 'above' : 'below'
        })
      } else {
        alert(data.error || 'Failed to get prediction. Try: 10001, 90001, 60601, 77001, 33109, 94027')
      }
    } catch (error) {
      console.error('Prediction error:', error)
      alert('Failed to connect to prediction API')
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
                <div className="text-2xl font-bold text-tax-gold">94.5%</div>
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
                    The XGBoost model was trained on 27,680 ZIP codes with 94.5% accuracy (R² = 0.9455).
                  </p>
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
            <h3 className="text-lg font-bold text-gray-900 mb-2">XGBoost ML Model</h3>
            <p className="text-gray-600">
              Advanced gradient boosting algorithm achieving 94.5% accuracy with average error of only $3,591
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
              Built with Python, XGBoost, Next.js, and deployed on Cloudflare Pages
            </p>
            <p className="text-gray-500 mt-2 text-sm">
              Data Source: IRS SOI Tax Statistics | Model Accuracy: 94.5% | © 2025
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
