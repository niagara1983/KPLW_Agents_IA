#!/usr/bin/env python3
"""
KPLW Strategic Innovations - Systeme Multi-Agents IA
====================================================
Point d'entree principal.

Usage :
  python main.py                          # Mode interactif
  python main.py --brief "Mon projet..."  # Mode direct
  python main.py --demo                   # Mode demonstration
  python main.py --file brief.txt         # Depuis un fichier
"""

import argparse
import sys
import os
from datetime import datetime

# Ajouter le repertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# KPLWOrchestrator removed - system is now RFP-specific only
# from agents import KPLWOrchestrator


def print_banner():
    """Affiche la banniere KPLW."""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        KPLW STRATEGIC INNOVATIONS INC.                   ║
    ║        Systeme Multi-Agents IA v1.0                      ║
    ║                                                          ║
    ║        TIMBO  |  ZAT  |  MARY  |  RANA                   ║
    ║                                                          ║
    ║  Strategic Intelligence. Sovereign Capability.            ║
    ║  Measurable Impact.                                      ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)


def save_results(state: dict, output_dir: str = "outputs", format: str = "md"):
    """Sauvegarde les resultats dans des fichiers (supports multiple formats)."""
    os.makedirs(output_dir, exist_ok=True)
    project_id = state.get("project_id", "KPLW-unknown")

    # Sauvegarder chaque output d'agent
    files_saved = []

    if state.get("timbo_analysis"):
        path = os.path.join(output_dir, f"{project_id}_1_TIMBO_analyse.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Analyse TIMBO\n## Projet : {project_id}\n\n")
            f.write(state["timbo_analysis"])
        files_saved.append(path)

    if state.get("zat_blueprint"):
        path = os.path.join(output_dir, f"{project_id}_2_ZAT_blueprint.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Blueprint ZAT\n## Projet : {project_id}\n\n")
            f.write(state["zat_blueprint"])
        files_saved.append(path)

    if state.get("tess_team_profiles"):
        path = os.path.join(output_dir, f"{project_id}_2.5_TESS_team_profiles.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Profils d'Équipe TESS\n## Projet : {project_id}\n\n")
            f.write(state["tess_team_profiles"])
        files_saved.append(path)

    if state.get("mary_deliverable"):
        path = os.path.join(output_dir, f"{project_id}_3_MARY_livrable.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Livrable MARY\n## Projet : {project_id}\n\n")
            f.write(state["mary_deliverable"])
        files_saved.append(path)

    if state.get("rana_evaluation"):
        path = os.path.join(output_dir, f"{project_id}_4_RANA_evaluation.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Evaluation RANA\n## Projet : {project_id}\n\n")
            f.write(state["rana_evaluation"])
        files_saved.append(path)

    # Compliance matrix (RFP mode)
    if state.get("compliance_matrix"):
        path = os.path.join(output_dir, f"{project_id}_COMPLIANCE_MATRIX.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(state["compliance_matrix"])
        files_saved.append(path)

    # Rapport complet
    path = os.path.join(output_dir, f"{project_id}_RAPPORT_COMPLET.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# RAPPORT COMPLET - {project_id}\n")
        f.write(f"**Date** : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Statut** : {state.get('status', 'N/A').upper()}\n")
        f.write(f"**Score RANA** : {state.get('rana_score', 'N/A')}/100\n")
        f.write(f"**Iterations** : {state.get('iteration_count', 0)}\n")

        # RFP-specific info
        if state.get("compliance_score"):
            f.write(f"**Compliance** : {state['compliance_score']:.1f}%\n")

        f.write("\n---\n\n")

        f.write("## 1. ANALYSE TIMBO\n\n")
        f.write(state.get("timbo_analysis", "Non disponible") + "\n\n")
        f.write("---\n\n")

        f.write("## 2. BLUEPRINT ZAT\n\n")
        f.write(state.get("zat_blueprint", "Non disponible") + "\n\n")
        f.write("---\n\n")

        if state.get("tess_team_profiles"):
            f.write("## 2.5. PROFILS D'ÉQUIPE TESS\n\n")
            f.write(state["tess_team_profiles"] + "\n\n")
            f.write("---\n\n")

        f.write("## 3. LIVRABLE MARY\n\n")
        f.write(state.get("mary_deliverable", "Non disponible") + "\n\n")
        f.write("---\n\n")

        f.write("## 4. EVALUATION RANA\n\n")
        f.write(state.get("rana_evaluation", "Non disponible") + "\n\n")
        f.write("---\n\n")

        # RFP compliance
        if state.get("compliance_matrix"):
            f.write("## 5. MATRICE DE CONFORMITÉ\n\n")
            f.write(state["compliance_matrix"] + "\n\n")
            f.write("---\n\n")

        f.write("## JOURNAL DU WORKFLOW\n\n")
        for log in state.get("workflow_log", []):
            f.write(f"- {log}\n")

        # Cost summary
        if state.get("cost_summary"):
            f.write("\n---\n\n")
            f.write("## COÛTS\n\n")
            cost = state["cost_summary"]
            f.write(f"**Total**: ${cost.get('total_cost', 0):.2f}\n")
            f.write(f"**Appels**: {cost.get('num_calls', 0)}\n")

    files_saved.append(path)

    print(f"\n  Fichiers sauvegardes dans '{output_dir}/' :")
    for f in files_saved:
        print(f"    -> {f}")

    return files_saved


def run_demo():
    """Execute une demonstration avec un projet exemple."""
    demo_brief = """
    PROJET : Strategie de transformation numerique pour le Ministere de l'Economie
    Numerique de la Republique du Cameroun.

    CONTEXTE : Le Ministere souhaite accelerer la transformation numerique du pays
    avec un plan strategique sur 5 ans. Le budget previsionnel est de 50 millions USD
    finances par la Banque Mondiale et la BAD.

    OBJECTIFS :
    1. Diagnostiquer la maturite numerique actuelle du pays
    2. Concevoir une strategie nationale de transformation numerique
    3. Proposer un plan d'implementation avec jalons et indicateurs
    4. Identifier les risques et strategies de mitigation

    LIVRABLES ATTENDUS :
    - Rapport de diagnostic (maturite numerique)
    - Document de strategie nationale
    - Plan d'implementation detaille
    - Cadre de suivi-evaluation

    DELAI : 8 semaines
    CLIENT : Ministere de l'Economie Numerique, Republique du Cameroun
    """
    return demo_brief


def run_interactive():
    """Mode interactif : l'utilisateur saisit son brief."""
    print("\n  Decrivez votre projet (terminez par une ligne vide) :\n")
    lines = []
    while True:
        try:
            line = input("  > ")
            if line.strip() == "":
                if lines:
                    break
                continue
            lines.append(line)
        except EOFError:
            break

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="KPLW Strategic Innovations - Systeme Multi-Agents IA & RFP Generator"
    )
    # Original mode arguments
    parser.add_argument("--brief", type=str, help="Brief du projet (texte direct)")
    parser.add_argument("--file", type=str, help="Fichier contenant le brief du projet")
    parser.add_argument("--demo", action="store_true", help="Lancer avec le projet demo")

    # RFP mode arguments (NEW)
    parser.add_argument("--rfp", action="store_true", help="Mode RFP: analyse et reponse a un appel d'offres")
    parser.add_argument("--rfp-files", nargs="+", help="Fichiers RFP (PDF, DOCX, MD)")
    parser.add_argument("--team-cvs", nargs="+", help="Fichiers CV de l'equipe (PDF, DOCX) - optionnel")
    parser.add_argument("--template", type=str, default="government_canada",
                       help="Template de proposition: government_canada, corporate, consulting, etc.")
    parser.add_argument("--format", type=str, default="md",
                       help="Format de sortie: md, docx, pdf, all")

    parser.add_argument("--output", type=str, default="outputs", help="Repertoire de sortie")

    # Cost tracking
    parser.add_argument("--cost-report", action="store_true", help="Generate cost report from all runs")

    args = parser.parse_args()

    print_banner()

    # Cost Report Mode
    if args.cost_report:
        from llm.cost_tracker_file import CostTrackerFile

        print("\n  [COST REPORT] Generating cost report...\n")
        tracker = CostTrackerFile("costs_history.json")

        # Get totals
        totals = tracker.get_total()
        print(f"  Total accumulated cost: ${totals['total_cost']:.4f}")
        print(f"  Total API calls: {totals['total_calls']:,}")
        print(f"  Total runs: {totals['run_count']}")

        # Generate report
        report_path = os.path.join(args.output, "COST_REPORT.md")
        tracker.generate_report(report_path)

        print(f"\n  Full report saved to: {report_path}\n")
        return

    # RFP Mode (NEW)
    if args.rfp:
        if not args.rfp_files:
            print("  [ERREUR] Mode RFP requis --rfp-files")
            print("  Exemple: python main.py --rfp --rfp-files rfp.pdf annexe.docx")
            sys.exit(1)

        print(f"\n  [MODE RFP] Analyse de {len(args.rfp_files)} document(s)")
        print(f"  Template: {args.template}")
        print(f"  Format sortie: {args.format}")
        if args.team_cvs:
            print(f"  Team CVs: {len(args.team_cvs)} fichier(s)")

        # Import RFP orchestrator
        try:
            from agents.rfp_orchestrator import RFPOrchestrator
        except ImportError:
            print("  [ERREUR] Module RFP non disponible.")
            print("  Verifiez que agents/rfp_orchestrator.py est present.")
            sys.exit(1)

        # Run RFP workflow
        orchestrator = RFPOrchestrator()
        state = orchestrator.run_rfp(
            rfp_files=args.rfp_files,
            template_name=args.template,
            output_formats=args.format.split(','),
            team_cvs=args.team_cvs
        )

        # Save results
        save_results(state, args.output, format=args.format)

        print(f"\n  [RFP] Workflow termine. Consultez '{args.output}/' pour les resultats.")

        # Print generated files summary
        if state.get("generated_files"):
            print(f"\n  Fichiers generes:")
            for fmt, path in state["generated_files"].items():
                print(f"    • {fmt.upper()}: {path}")

        # Print compliance summary
        if state.get("compliance_matrix"):
            print(f"\n  Compliance: {state['compliance_score']:.1f}%")
            gaps = state.get("compliance_gaps", [])
            if gaps:
                print(f"  Attention: {len(gaps)} requirements non-adresses")

        return

    # Original Mode (general consulting project) - REMOVED
    # System is now RFP-specific only
    print("\n  [INFO] KPLW system is now RFP-specific.")
    print("  Use --rfp flag with --rfp-files to process RFP documents.")
    print("\n  Example:")
    print("    python main.py --rfp --rfp-files rfp.pdf")
    print("    python main.py --rfp --rfp-files rfp.pdf --template government_canada")
    print("\n  For help: python main.py --help")
    sys.exit(0)


if __name__ == "__main__":
    main()
