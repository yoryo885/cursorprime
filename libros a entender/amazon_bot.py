"""Bot Amazon/KDP — investigación y asistente de publicación."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.config import RESUMENES_DIR


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bot Amazon: research + asistente KDP")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("research", help="Autocompletado + competidores → kdp/")
    r.add_argument("--slug", required=True)
    r.add_argument("--mercado", default="MX", choices=["MX", "ES"])
    r.add_argument("--headless", action="store_true")

    k = sub.add_parser("kdp", help="Abre KDP + panel copiar listing")
    k.add_argument("--slug", required=True)

    return p.parse_args()


def main() -> None:
    args = parse_args()
    slug_dir = RESUMENES_DIR / args.slug
    if not slug_dir.is_dir():
        print(f"❌ No existe resumenes/{args.slug}/", file=sys.stderr)
        sys.exit(1)

    if args.cmd == "research":
        from src.marketing.bot.amazon_research import AmazonResearchBot

        AmazonResearchBot().run(args.slug, headless=args.headless)
        # refrescar inteligencia
        try:
            from src.marketing.agents.audience_intelligence_agent import AudienceIntelligenceAgent
            from src.marketing.agents.context_agent import ContextAgent
            from src.marketing.pdf_reader import extract_pdf_content

            pdfs = sorted(slug_dir.glob("*.pdf"), key=lambda p: p.stat().st_size, reverse=True)
            if pdfs:
                pdf = extract_pdf_content(pdfs[0])
                brief = ContextAgent().run(pdf=pdf)
                intel, path = AudienceIntelligenceAgent().run(brief, pdf, post_listing=True)
                score = intel.comparativa.get("discoverability_score", {}).get("score")
                print(f"✓ Discoverability actualizado: {score}/10 → {path.name}")
        except Exception as err:
            print(f"⚠️  Inteligencia no actualizada: {err}")

    elif args.cmd == "kdp":
        from src.marketing.bot.kdp_assistant import KDPAssistantBot

        KDPAssistantBot().run(args.slug)


if __name__ == "__main__":
    main()
