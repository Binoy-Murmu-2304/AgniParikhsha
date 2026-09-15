import os

filepath = r"c:\Users\binoy\Videos\dff\AstraGuard-main (1)\AstraGuard-main\dashboard\src\app\page.tsx"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

target = '<div className="p-3 bg-slate-900 rounded-lg border border-slate-800 text-teal-300 mt-4">\n                        <strong>Matched Failure Kinetics:</strong> {shapData.matched_failure_mechanism}\n                      </div>'

replacement = '''<div className="p-3 bg-slate-900 rounded-lg border border-slate-800 text-teal-300 mt-4">
                        <strong>Matched Failure Kinetics:</strong> {shapData.matched_failure_mechanism}
                      </div>
                      <button
                        onClick={() => downloadQualificationCert(selectedComponent || { component_id: 'COMP-2026-001', device_family: 'DIGITAL_IC', iddq_0h: 11.2, iddq_24h: 12.1, predicted_168h: 14.8, risk_tier: 'GREEN_AUTO_PASS' })}
                        className="mt-4 w-full py-2.5 px-4 bg-orange-600 hover:bg-orange-500 text-white font-bold text-xs rounded-lg shadow-lg flex items-center justify-center gap-2 transition-all cursor-pointer"
                      >
                        🔥 Download ISRO Spaceflight Qualification Certificate (PDF)
                      </button>'''

if "Download ISRO Spaceflight Qualification Certificate" not in content:
    content = content.replace(target, replacement)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated page.tsx with PDF download button successfully.")
else:
    print("PDF download button already present.")
