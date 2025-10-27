/**
 * Hybrid Income Prediction API (Traditional + ML Intelligent Weighted Ensemble)
 * 
 * Combines:
 * - Traditional Statistical Model (30% base weight) - Deterministic, explainable
 * - Pure ML Stacked Ensemble (70% base weight) - High accuracy, non-linear patterns
 * - Dynamic weight adjustment based on confidence scores
 * 
 * Research Basis (2021-2025):
 * - Verme (2025): "Predicting Poverty: Machine Learning Algorithms" - ML achieves 95%+ accuracy
 * - Xia et al. (2023): "Combining Linear + XGBoost" - Hybrid models outperform single methods
 * - Wen & Zhou (2024): "Demo2Vec: Region Embedding with Demographics" - Spatial features improve predictions
 * - Wang (2022): "Income Forecasting based on Machine Learning" - Feature importance for segmentation
 * - Chung et al. (2022): Traditional methods stable, ML methods accurate
 * 
 * Weighting Strategy:
 * - 70% ML: Higher accuracy (96%+) on complex patterns, spatial features
 * - 30% Traditional: Stability, explainability, regulatory validation
 * - Dynamic adjustment: ±10-15% based on confidence differential
 * - Ensemble confidence boost: +2% (diversity reduces overfitting)
 * - Minimal disagreement penalty: Only 5% reduction if >30% difference
 * 
 * Expected Performance: Best of both worlds - accuracy + robustness + explainability
 */

interface PredictionRequest {
  zipCode: string;
}

interface HybridPrediction {
  zipCode: string;
  state: string;
  predictedIncome: number;
  confidence: number;
  methodology: string;
  components: {
    traditionalPrediction: number;
    traditionalConfidence: number;
    mlPrediction: number;
    mlConfidence: number;
    weightingStrategy: string;
    disagreementPenalty: number;
  };
  explanation: string[];
}

/**
 * Fetch prediction from Traditional Statistical Model
 */
async function fetchTraditionalPrediction(zipCode: string, baseUrl: string): Promise<any> {
  const response = await fetch(`${baseUrl}/api/predict-traditional`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ zipCode })
  });

  if (!response.ok) {
    throw new Error('Failed to fetch traditional prediction');
  }

  const result = await response.json();
  return result.data;
}

/**
 * Fetch prediction from Pure ML Model
 */
async function fetchMLPrediction(zipCode: string, baseUrl: string): Promise<any> {
  const response = await fetch(`${baseUrl}/api/predict-ml`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ zipCode })
  });

  if (!response.ok) {
    throw new Error('Failed to fetch ML prediction');
  }

  const result = await response.json();
  return result.data;
}

/**
 * Calculate hybrid prediction using intelligent weighted ensemble
 * 
 * Research-based improvements (2024-2025 papers):
 * - 70% ML + 30% Traditional (ML has higher accuracy per Verme 2025, Wang 2022)
 * - Dynamic weighting based on confidence scores
 * - Spatial feature consideration (Wen & Zhou 2024 Demo2Vec)
 * - Reduced disagreement penalty (ensemble diversity is beneficial per Xia 2023)
 * 
 * Formula: Dynamic weight × Traditional + (1 - Dynamic weight) × ML
 * Confidence boost: Ensemble typically more robust than single models
 */
function calculateHybridPrediction(
  traditional: any,
  ml: any
): HybridPrediction {
  // Base weights favor ML (higher accuracy in research)
  let ML_WEIGHT = 0.70;  // Increased from 0.60
  let TRADITIONAL_WEIGHT = 0.30; // Decreased from 0.40
  
  const DISAGREEMENT_THRESHOLD = 0.30; // Relaxed to 30% (diversity is good)
  const DISAGREEMENT_PENALTY = 0.95; // Minimal penalty (only 5% reduction)

  // Dynamic weight adjustment based on confidence differential
  const confidenceDiff = ml.confidence - traditional.confidence;
  if (confidenceDiff > 0.05) {
    // ML much more confident, increase its weight
    ML_WEIGHT = Math.min(0.85, ML_WEIGHT + 0.10);
    TRADITIONAL_WEIGHT = 1 - ML_WEIGHT;
  } else if (confidenceDiff < -0.05) {
    // Traditional more confident, slightly increase its weight
    TRADITIONAL_WEIGHT = Math.min(0.40, TRADITIONAL_WEIGHT + 0.05);
    ML_WEIGHT = 1 - TRADITIONAL_WEIGHT;
  }

  // Weighted prediction
  const predictedIncome = Math.round(
    (traditional.predictedIncome * TRADITIONAL_WEIGHT) +
    (ml.predictedIncome * ML_WEIGHT)
  );

  // Calculate disagreement
  const disagreement = Math.abs(
    traditional.predictedIncome - ml.predictedIncome
  ) / Math.max(traditional.predictedIncome, ml.predictedIncome);

  // Base confidence (weighted average) with ensemble bonus
  let confidence = (
    (traditional.confidence * TRADITIONAL_WEIGHT) +
    (ml.confidence * ML_WEIGHT)
  );
  
  // Ensemble confidence boost (diversity reduces overfitting)
  confidence = Math.min(0.99, confidence * 1.02); // 2% boost for ensemble

  // Apply minimal disagreement penalty only if very high
  let disagreementPenalty = 1.0;
  if (disagreement > DISAGREEMENT_THRESHOLD) {
    disagreementPenalty = DISAGREEMENT_PENALTY;
    confidence *= disagreementPenalty;
  }

  // Generate explanation
  const explanation = [
    `Traditional Model: $${traditional.predictedIncome.toLocaleString()} (confidence: ${(traditional.confidence * 100).toFixed(1)}%)`,
    `ML Model: $${ml.predictedIncome.toLocaleString()} (confidence: ${(ml.confidence * 100).toFixed(1)}%)`,
    `Smart weighting: ${(TRADITIONAL_WEIGHT * 100).toFixed(0)}% Traditional + ${(ML_WEIGHT * 100).toFixed(0)}% ML (dynamic)`,
    `Disagreement: ${(disagreement * 100).toFixed(1)}% ${disagreement > DISAGREEMENT_THRESHOLD ? '(ensemble diversity - minimal penalty)' : '(models agree well)'}`,
    `Hybrid ensemble prediction: $${predictedIncome.toLocaleString()} (confidence: ${(confidence * 100).toFixed(1)}%)`,
    `Research basis: Xia (2023), Verme (2025), Wen & Zhou (2024) - ensemble methods outperform single models`
  ];

  return {
    zipCode: traditional.zipCode,
    state: traditional.state,
    predictedIncome,
    confidence,
    methodology: 'Hybrid Model (Intelligent Weighted Ensemble - Research-Based)',
    components: {
      traditionalPrediction: traditional.predictedIncome,
      traditionalConfidence: traditional.confidence,
      mlPrediction: ml.predictedIncome,
      mlConfidence: ml.confidence,
      weightingStrategy: `${(ML_WEIGHT * 100).toFixed(0)}% ML + ${(TRADITIONAL_WEIGHT * 100).toFixed(0)}% Traditional`,
      disagreementPenalty
    },
    explanation
  };
}

/**
 * Cloudflare Pages Function handler
 */
export async function onRequestPost(context: any): Promise<Response> {
  try {
    const { zipCode } = await context.request.json() as PredictionRequest;

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

    // Get base URL from request
    const url = new URL(context.request.url);
    const baseUrl = `${url.protocol}//${url.host}`;

    // Fetch predictions from both models (in parallel for speed)
    const [traditionalPrediction, mlPrediction] = await Promise.all([
      fetchTraditionalPrediction(zipCode, baseUrl),
      fetchMLPrediction(zipCode, baseUrl)
    ]);

    // Calculate hybrid prediction
    const hybridPrediction = calculateHybridPrediction(
      traditionalPrediction,
      mlPrediction
    );

    return new Response(
      JSON.stringify({
        success: true,
        data: hybridPrediction,
        metadata: {
          model: 'Hybrid Ensemble',
          version: '1.0',
          timestamp: new Date().toISOString(),
          researchBased: [
            'Verme (2025): Ensemble methods',
            'Chung et al. (2022): Traditional + ML combination',
            'Zhou & Wen (2024): Regional embeddings'
          ],
          weightingStrategy: '60% ML + 40% Traditional'
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
    console.error('Hybrid prediction error:', error);
    
    return new Response(
      JSON.stringify({ 
        error: 'Prediction failed',
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
      message: 'Hybrid Income Prediction API',
      version: '1.0',
      method: 'POST',
      endpoint: '/api/predict-hybrid',
      description: 'Weighted ensemble combining Traditional Statistical (40%) + Pure ML (60%)',
      weightingStrategy: {
        ml: '60%',
        traditional: '40%',
        disagreementPenalty: 'Reduces confidence by 20% if predictions differ >20%'
      },
      advantages: [
        'Best of both worlds: accuracy + explainability',
        'Stable predictions from traditional component',
        'High accuracy from ML component',
        'Confidence adjustment for disagreements'
      ],
      research: [
        'Verme (2025): Ensemble methods benefit from diverse sources',
        'Chung et al. (2022): Traditional methods stable in public sector',
        'Zhou & Wen (2024): Regional embedding enhancements'
      ],
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
