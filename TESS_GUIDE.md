# TESS Agent - Team Expertise Selection Specialist

## Overview

TESS analyzes team member CVs against RFP requirements and generates **tailored team profiles** that highlight only relevant experience for the specific proposal.

## Why TESS?

✅ **Tailored, not generic** - Extracts only experience relevant to THIS RFP
✅ **Compliance-focused** - Maps team experience to RFP requirements
✅ **Concise** - ½-1 page per person (not full 3-page CVs)
✅ **Gap detection** - Identifies missing qualifications early
✅ **Automated** - No manual CV customization needed

## How It Works

```
RFP Requirements → TESS → Tailored Team Profiles → MARY → Proposal
```

### Workflow Position:

1. **TIMBO** - Analyzes RFP requirements
2. **ZAT** - Designs proposal structure
3. **TESS** - Analyzes CVs and creates tailored profiles ⬅️ NEW
4. **MARY** - Writes proposal (with TESS profiles integrated)
5. **RANA** - Validates quality

## Usage

### Basic Usage (No Team CVs):

```bash
python main.py --rfp --rfp-files rfp.pdf
```

### With Team CVs:

```bash
python main.py --rfp \
  --rfp-files rfp.pdf \
  --team-cvs cv_chef_projet.pdf cv_auditeur_senior.pdf cv_analyste.pdf
```

### Full Example:

```bash
python main.py --rfp \
  --rfp-files "Appel-de-propositions-audit-FCFA.pdf" \
  --team-cvs cvs/jean_dupont.pdf cvs/marie_martin.pdf cvs/ahmed_kane.pdf \
  --template consulting \
  --format md,docx
```

## What TESS Produces

### 1. Team Summary

```markdown
| Nom | Rôle | Exp. pertinente | Certifications | Score |
|-----|------|-----------------|----------------|-------|
| Jean Dupont | Chef de projet | 12 ans | CPA, CIA | 9/10 |
| Marie Martin | Auditeur senior | 8 ans | CPA | 8/10 |
```

### 2. Requirement Coverage

```markdown
✓ R005: "Chef de projet avec 10+ ans expérience audit" → Couvert par Jean Dupont
✓ R012: "Certification CPA requise" → Couvert par Jean Dupont, Marie Martin
⚠ R018: "Expérience audit IT" → Partiellement couvert - [mitigation suggérée]
```

### 3. Individual Tailored Profiles

For each team member:

```markdown
### Jean Dupont, CPA, CIA

**Rôle proposé**: Chef de projet d'audit

**Expérience pertinente**:
- Audit financier FCFA 5M pour Ministère Éducation (2022-2023)
  → Adresse requirements R005, R012
  → Score: 9/10

- Gestion programme BAD 3M FCFA (2020-2021)
  → Adresse requirement R008
  → Score: 8/10

**Compétences clés**:
- Audit secteur public: 12 ans (Expert)
- Normes FCFA: Expert
- Gestion équipe 5-10 personnes: Confirmé

**Certifications**: CPA (2010), CIA (2015)

**Pourquoi qualifié**: 12 ans d'expérience en audit financier du secteur
public avec expertise spécifique en programmes financés FCFA...
```

## Output Files

When TESS is used, you'll get:

1. `{project_id}_2.5_TESS_team_profiles.md` - Standalone TESS output
2. `{project_id}_3_MARY_livrable.md` - Proposal with TESS profiles integrated
3. `{project_id}_RAPPORT_COMPLET.md` - Full report including TESS section

## TESS Logic

### Relevance Scoring (0-10):

- **10**: Nearly identical project (same sector, type, scale)
- **8-9**: Highly relevant (similar sector or type)
- **6-7**: Relevant (transferable skills)
- **4-5**: Moderately relevant
- **0-3**: Not relevant (excluded from profile)

### What Gets Included:

✅ Recent experience (last 5 years prioritized)
✅ Experience directly addressing RFP requirements
✅ Relevant certifications only
✅ Quantified achievements (budgets, durations, results)

### What Gets Excluded:

❌ Irrelevant past jobs (e.g., "taught marketing 2010-2012" for audit RFP)
❌ Non-applicable certifications
❌ Generic descriptions without quantification

## Gap Detection

TESS identifies missing qualifications:

```markdown
⚠️ GAPS IDENTIFIED:
- R025: "Certification CISA" - No team member has this
  Mitigation: [Suggest training or subcontractor]
```

## Cost Considerations

- TESS runs **once** per RFP (not in iteration loop)
- Typical cost: $0.05-0.15 per CV analyzed (depending on length)
- For 3 CVs: ~$0.15-0.45 additional cost
- **ROI**: Significantly improves "Team Qualifications" section (15-30% of RFP score)

## Best Practices

### CV Naming:

Name CV files clearly:
```
cv_jean_dupont_chef_projet.pdf
cv_marie_martin_auditeur_senior.pdf
```

### CV Format:

- **PDF preferred** (better parsing)
- DOCX also supported
- Ensure CVs have clear sections (Experience, Education, Certifications)

### When to Use TESS:

✅ **Use when**:
- RFP has team/personnel requirements
- RFP evaluates "Team Qualifications" (most do)
- You have detailed CVs available

❌ **Skip when**:
- RFP doesn't evaluate team
- No team CVs available (TESS will be skipped automatically)
- Solo consultant (no team)

## Example Output in Proposal

TESS profiles get integrated into MARY's proposal:

```markdown
## 5. NOTRE ÉQUIPE

### 5.1 Composition de l'équipe

Notre équipe combine expertise technique et connaissance approfondie...

[TESS profiles automatically inserted here]

### Jean Dupont - Chef de projet
[Tailored profile from TESS]

### Marie Martin - Auditeur senior
[Tailored profile from TESS]

...
```

## Troubleshooting

**Issue**: CV parsing fails

```
⚠ Warning: Could not parse cv_name.pdf
```

**Solution**:
- Ensure CV is valid PDF/DOCX (not scanned image)
- Try converting to PDF if DOCX fails
- Check file permissions

**Issue**: TESS finds no relevant experience

```
⚠ Gaps identified: [long list]
```

**Solution**:
- CVs may not match RFP requirements
- Consider different team members
- TESS output will show what's missing - use for recruiting/training

## Advanced Usage

### Multiple CV Formats:

```bash
--team-cvs cvs/*.pdf  # All PDFs in cvs/ directory (bash glob)
```

### With Cost Tracking:

```bash
python main.py --rfp \
  --rfp-files rfp.pdf \
  --team-cvs cv1.pdf cv2.pdf cv3.pdf

# Then check cost
python main.py --cost-report
```

## Next Steps

After TESS implementation, consider:

1. **CV library**: Maintain team CV database for reuse
2. **Template CVs**: Create structured CV templates for consistent parsing
3. **Gap analysis**: Use TESS gaps to guide hiring/training decisions

## Questions?

TESS integrates seamlessly - just add `--team-cvs` to your existing workflow!
