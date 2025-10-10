/**
 * Method Comparison API
 * 
 * Calls all 3 prediction methods in parallel and provides comprehensive comparison:
 * 1. Traditional Statistical Model (econometric formulas)
 * 2. Pure ML Model (stacked ensemble)
 * 3. Hybrid Model (weighted combination)
 * 
 * Returns:
 * - All predictions with confidence scores
 * - Performance comparison (accuracy, speed, confidence)
 * - Variance analysis and agreement metrics
 * - Recommendation based on context
 * - Visualization data for charts
 */

interface ComparisonRequest {
  zipCode: string;
}

interface MethodResult {
  income: number;
  confidence: number;
  timeMs: number;
  methodology: string;
}

interface ComparisonResponse {
  zipCode: string;
  state: string;
  methods: {
    traditional: MethodResult;
    ml: MethodResult;
    hybrid: MethodResult;
  };
  comparison: {
    variance: number;
    standardDeviation: number;
    range: {
      min: number;
      max: number;
      spread: number;
    };
    agreement: 'high' | 'medium' | 'low';
    recommended: 'traditional' | 'ml' | 'hybrid';
    recommendationReason: string;
  };
  charts: {
    methodComparison: Array<{
      method: string;
      income: number;
      confidence: number;
    }>;
    confidenceComparison: Array<{
      method: string;
      confidence: number;
    }>;
    agreementVisualization: Array<{
      method: string;
      deviation: number;
    }>;
  };
}

/**
 * Fetch prediction from a specific method with timing
 */
async function fetchMethodPrediction(
  method: 'traditional' | 'ml' | 'hybrid',
  zipCode: string
): Promise<{ data: any; timeMs: number }> {
  const startTime = performance.now();
  
  const endpoint = `/api/predict-${method}`;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ zipCode })
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch ${method} prediction: ${response.statusText}`);
  }

  const result = await response.json();
  const endTime = performance.now();
  
  return {
    data: result.data,
    timeMs: Math.round(endTime - startTime)
  };
}

/**
 * Calculate agreement level between predictions
 */
function calculateAgreement(predictions: number[]): 'high' | 'medium' | 'low' {
  const mean = predictions.reduce((a, b) => a + b, 0) / predictions.length;
  const maxDeviation = Math.max(
    ...predictions.map(p => Math.abs(p - mean) / mean)
  );

  if (maxDeviation < 0.05) return 'high'; // <5% deviation
  if (maxDeviation < 0.15) return 'medium'; // <15% deviation
  return 'low'; // >=15% deviation
}

/**
 * Generate recommendation based on results
 */
function generateRecommendation(
  traditional: MethodResult,
  ml: MethodResult,
  hybrid: MethodResult,
  agreement: 'high' | 'medium' | 'low'
): { recommended: 'traditional' | 'ml' | 'hybrid'; reason: string } {
  // If high agreement, recommend hybrid (best of both worlds)
  if (agreement === 'high') {
    return {
      recommended: 'hybrid',
      reason: 'All methods agree closely. Hybrid combines the best of both approaches with highest confidence.'
    };
  }

  // If medium agreement, prioritize by confidence
  if (agreement === 'medium') {
    const maxConfidence = Math.max(
      traditional.confidence,
      ml.confidence,
      hybrid.confidence
    );

    if (hybrid.confidence === maxConfidence) {
      return {
        recommended: 'hybrid',
        reason: 'Moderate agreement between methods. Hybrid balances accuracy and explainability.'
      };
    }

    if (ml.confidence === maxConfidence) {
      return {
        recommended: 'ml',
        reason: 'ML model has highest confidence with 95.01% historical accuracy on IRS data.'
      };
    }

    return {
      recommended: 'traditional',
      reason: 'Traditional model provides stable, explainable predictions with high confidence.'
    };
  }

  // Low agreement - recommend traditional for safety
  return {
    recommended: 'traditional',
    reason: 'Methods disagree significantly. Traditional model provides most explainable and stable prediction.'
  };
}

/**
 * Cloudflare Pages Function handler
 */
export async function onRequestPost(context: any): Promise<Response> {
  try {
    const { zipCode } = await context.request.json() as ComparisonRequest;

    // Validate ZIP code
    if (!zipCode || !/^\d{5}$/.test(zipCode)) {
      return new Response(
        JSON.stringify({ 
          error: 'Invalid ZIP code. Please provide a 5-digit ZIP code.' 
        }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // Fetch all predictions in parallel
    const [traditionalResult, mlResult, hybridResult] = await Promise.all([
      fetchMethodPrediction('traditional', zipCode),
      fetchMethodPrediction('ml', zipCode),
      fetchMethodPrediction('hybrid', zipCode)
    ]);

    // Extract predictions
    const predictions = [
      traditionalResult.data.predictedIncome,
      mlResult.data.predictedIncome,
      hybridResult.data.predictedIncome
    ];

    // Calculate statistics
    const mean = predictions.reduce((a, b) => a + b, 0) / predictions.length;
    const variance = predictions.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / predictions.length;
    const stdDev = Math.sqrt(variance);
    const min = Math.min(...predictions);
    const max = Math.max(...predictions);
    const spread = max - min;

    // Calculate agreement
    const agreement = calculateAgreement(predictions);

    // Generate recommendation
    const { recommended, reason } = generateRecommendation(
      {
        income: traditionalResult.data.predictedIncome,
        confidence: traditionalResult.data.confidence,
        timeMs: traditionalResult.timeMs,
        methodology: traditionalResult.data.methodology
      },
      {
        income: mlResult.data.predictedIncome,
        confidence: mlResult.data.confidence,
        timeMs: mlResult.timeMs,
        methodology: mlResult.data.methodology
      },
      {
        income: hybridResult.data.predictedIncome,
        confidence: hybridResult.data.confidence,
        timeMs: hybridResult.timeMs,
        methodology: hybridResult.data.methodology
      },
      agreement
    );

    // Prepare response
    const response: ComparisonResponse = {
      zipCode,
      state: traditionalResult.data.state,
      methods: {
        traditional: {
          income: traditionalResult.data.predictedIncome,
          confidence: traditionalResult.data.confidence,
          timeMs: traditionalResult.timeMs,
          methodology: traditionalResult.data.methodology
        },
        ml: {
          income: mlResult.data.predictedIncome,
          confidence: mlResult.data.confidence,
          timeMs: mlResult.timeMs,
          methodology: mlResult.data.methodology
        },
        hybrid: {
          income: hybridResult.data.predictedIncome,
          confidence: hybridResult.data.confidence,
          timeMs: hybridResult.timeMs,
          methodology: hybridResult.data.methodology
        }
      },
      comparison: {
        variance: Math.round(variance),
        standardDeviation: Math.round(stdDev),
        range: {
          min: Math.round(min),
          max: Math.round(max),
          spread: Math.round(spread)
        },
        agreement,
        recommended,
        recommendationReason: reason
      },
      charts: {
        methodComparison: [
          {
            method: 'Traditional',
            income: traditionalResult.data.predictedIncome,
            confidence: traditionalResult.data.confidence
          },
          {
            method: 'Pure ML',
            income: mlResult.data.predictedIncome,
            confidence: mlResult.data.confidence
          },
          {
            method: 'Hybrid',
            income: hybridResult.data.predictedIncome,
            confidence: hybridResult.data.confidence
          }
        ],
        confidenceComparison: [
          {
            method: 'Traditional',
            confidence: traditionalResult.data.confidence
          },
          {
            method: 'Pure ML',
            confidence: mlResult.data.confidence
          },
          {
            method: 'Hybrid',
            confidence: hybridResult.data.confidence
          }
        ],
        agreementVisualization: [
          {
            method: 'Traditional',
            deviation: Math.abs(traditionalResult.data.predictedIncome - mean)
          },
          {
            method: 'Pure ML',
            deviation: Math.abs(mlResult.data.predictedIncome - mean)
          },
          {
            method: 'Hybrid',
            deviation: Math.abs(hybridResult.data.predictedIncome - mean)
          }
        ]
      }
    };

    return new Response(
      JSON.stringify({
        success: true,
        data: response,
        metadata: {
          version: '1.0',
          timestamp: new Date().toISOString(),
          totalExecutionTime: Math.max(
            traditionalResult.timeMs,
            mlResult.timeMs,
            hybridResult.timeMs
          ),
          description: 'Comprehensive comparison of all 3 prediction methods'
        }
      }),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'public, max-age=1800' // Cache for 30 minutes
        }
      }
    );
  } catch (error: any) {
    console.error('Comparison API error:', error);
    
    return new Response(
      JSON.stringify({ 
        error: 'Comparison failed',
        message: error.message || 'Unknown error occurred'
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

/**
 * GET request handler (for testing)
 */
export async function onRequestGet(context: any): Promise<Response> {
  return new Response(
    JSON.stringify({
      message: 'Method Comparison API',
      version: '1.0',
      method: 'POST',
      endpoint: '/api/compare-methods',
      description: 'Calls all 3 prediction methods and provides comprehensive comparison',
      methods: [
        'Traditional Statistical Model (econometric formulas)',
        'Pure ML Model (stacked ensemble, 95.01% accuracy)',
        'Hybrid Model (60% ML + 40% Traditional weighted ensemble)'
      ],
      returns: {
        predictions: 'All 3 method predictions with confidence scores',
        statistics: 'Variance, standard deviation, range analysis',
        agreement: 'High/Medium/Low agreement classification',
        recommendation: 'Best method based on context and agreement',
        charts: 'Visualization data for method comparison, confidence, agreement'
      },
      exampleRequest: {
        zipCode: '10001'
      }
    }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    }
  );
}
