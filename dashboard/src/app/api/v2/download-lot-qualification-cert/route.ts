import { NextRequest, NextResponse } from "next/server";
import { generateMasterLotCertPdf } from "@/lib/pdf-generator";

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json();
    const lotId = payload.lot_id || "ISRO_LOT_SAC_2026_01";
    const components = payload.components || [];

    const pdfBytes = await generateMasterLotCertPdf(lotId, components);

    return new NextResponse(Buffer.from(pdfBytes), {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="ISRO_Master_Lot_${lotId}_Cert.pdf"`,
      },
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: "Failed to generate master lot certificate: " + (err.message || String(err)) },
      { status: 500 }
    );
  }
}
