import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    dataset_id: "ASQD_2.5_ISRO_FLIGHT",
    source_type: "isro_htol_datalog",
    source_description: "ISRO PS #26170 Spaceflight Qualification Dataset",
    n_samples_total: 12000,
    validation_method: "5fold_cv_repeated_3x",
    checksum_sha256: "a3f89e21b7c4d5108e901f2a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c"
  });
}
