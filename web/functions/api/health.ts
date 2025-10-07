// Health check endpoint for Pages Function

export async function onRequestGet() {
  return new Response(
    JSON.stringify({
      status: 'healthy',
      service: 'Regional Income Prediction API',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      endpoints: {
        predict: '/api/predict (POST)',
        health: '/api/health (GET)'
      }
    }),
    {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    }
  );
}
