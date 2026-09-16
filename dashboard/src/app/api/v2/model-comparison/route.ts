import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    status: "success",
    benchmark_matrix: [
      { model_name: "AgniPariksha_XGBoost", mae_uA: 0.147, rmse_uA: 0.285, r2_score: 0.9957, defect_recall_pct: 100.0, chamber_hours_saved_pct: 71.4, status: "WINNER" },
      { model_name: "PINN_MLP_Neural_Network", mae_uA: 0.312, rmse_uA: 0.540, r2_score: 0.9812, defect_recall_pct: 98.2, chamber_hours_saved_pct: 68.1, status: "EVALUATED" },
      { model_name: "Random_Forest_Regressor", mae_uA: 0.485, rmse_uA: 0.890, r2_score: 0.9650, defect_recall_pct: 95.5, chamber_hours_saved_pct: 62.0, status: "EVALUATED" },
      { model_name: "Physics_Ridge_Baseline", mae_uA: 1.250, rmse_uA: 2.150, r2_score: 0.8910, defect_recall_pct: 88.0, chamber_hours_saved_pct: 45.0, status: "BASELINE" }
    ],
    recommended_model: "AgniPariksha_XGBoost",
    conformal_confidence_level: "95.0%"
  });
}
