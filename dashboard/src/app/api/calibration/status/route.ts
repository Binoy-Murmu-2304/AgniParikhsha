import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    status: "HEALTHY",
    n_updates: 12000,
    current_conformal_quantile: 0.95,
    recommend_retraining: false,
    reason: "Conformal coverage maintained at 95.0% target.",
    metrics: { coverage: 0.95, avg_width: 2.50 }
  });
}
