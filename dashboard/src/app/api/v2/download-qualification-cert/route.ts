import { NextRequest, NextResponse } from "next/server";
import { generateComponentCertPdf } from "@/lib/pdf-generator";

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json();
    const pdfBytes = await generateComponentCertPdf(payload);
    const compId = payload.component_id || "ISRO-SAC-2026-0001";

    return new NextResponse(Buffer.from(pdfBytes), {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="ISRO_Qualification_Cert_${compId}.pdf"`,
      },
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: "Failed to generate qualification certificate: " + (err.message || String(err)) },
      { status: 500 }
    );
  }
}
