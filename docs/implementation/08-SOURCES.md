# 08 — Sources, freshness and evidence boundaries

Reviewed: 9 October 2026. This is an implementation-source review, not a comprehensive competitor, legal or market investigation.

The original dossier is supplied by the user. Product scope comes from that dossier. The specific design changes in this kit are engineering recommendations; sources below inform them but do not validate the whole proposed system.

## Primary sources inspected

| ID | Source | What was checked | Consequence |
|---|---|---|---|
| S01 | [21st.dev](https://21st.dev/) | Component catalog and current copy/install workflow | Choose exact components during P6; check each author's terms |
| S02 | [21st navigation](https://21st.dev/community/components/s/navigation-menu) | Navigation discovery page | Source candidates, not a pre-approved implementation |
| S03 | [21st cards](https://21st.dev/community/components/s/card) | Card discovery page | Select a restrained pattern and adapt it |
| S04 | [Magic UI on 21st](https://21st.dev/@dillionverma/library/magic-ui) | Author collection | Inspect a candidate such as a counter; exact reuse still to be checked |
| S05 | [shadcn registry](https://ui.shadcn.com/docs/registry) | Source distribution model | Vendor permitted components and keep provenance |
| S06 | [MCP Streamable HTTP, 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) | Current transport revision differs from the dossier's lifecycle assumptions | Pin an SDK-supported revision and test compatibility |
| S07 | [MCP older transport specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) | Older HTTP/stdio description | Do not combine version-specific behaviours |
| S08 | [OpenTelemetry GenAI conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | Official page now directs readers to a separate GenAI conventions repository | Follow the current source and pin the import mapping |
| S09 | [OTel agent span conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) | Agent conventions marked Development in retrieved material | Do not treat evolving fields as a frozen universal replay contract |
| S10 | [statsmodels difference-of-proportions intervals](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.confint_proportions_2indep.html) | Independent binomial-sample assumption, diff comparison and Newcombe method | Specify the method explicitly; test API and assumptions |
| S11 | [Angelopoulos and Bates, conformal prediction introduction](https://arxiv.org/abs/2107.07511) | Primary methodological reference | Any later calibration claim must state its assumptions |
| S12 | [Docker none network driver](https://docs.docker.com/engine/network/drivers/none/) | Network isolation mechanism | Use an actual runtime boundary and test it; other isolation controls remain needed |
| S13 | [React Flow documentation](https://reactflow.dev/learn) | Official graph component documentation | Appropriate basis for interactive provenance nodes |
| S14 | [Motion for React](https://motion.dev/docs/react) | Official animation integration | Use focused transitions with reduced-motion behaviour |

Source-specific summary: the current MCP HTTP page describes a POST endpoint, request-scoped streaming and revision-dependent changes. That does not prescribe REWIND's application SSE API. Its local security guidance includes Origin validation, loopback binding and authentication.

The statsmodels function documents a comparison between two independent binomial samples. Using it is an implementation choice, not a guarantee that model runs are independent or that the experimental design is valid.

## Governance sources found, not fully validated

Official IMDA locations were found:
- [Agentic AI framework launch](https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/press-releases/2026/new-model-ai-governance-framework-for-agentic-ai)
- [Updated framework notice](https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/updated-model-ai-governance-framework-for-agentic-ai)
- [Framework PDF](https://www.imda.gov.sg/-/media/imda/files/about/emerging-tech-and-research/artificial-intelligence/mgf-for-agentic-ai.pdf)

The full notice/PDF text was not available through this retrieval. The existence of these official sources does **not** validate the dossier's exact v1.5 date, detailed clauses or a conformance claim. Before implementing clause-level mapping, retrieve and read the exact document/version, record its digest, and cite the applicable section.

No legal certification or applicability assessment is made by this kit. A future report may map implementation evidence to verified framework controls and must identify incomplete coverage.

## Dossier claims not adopted as established facts

Re-verify before a public pitch:
- “88%” incident prevalence and “61%” credential figures.
- Incident dates, CVE descriptions, download counts and vulnerability scores.
- “Nobody provides this” and “first in the world” competitor claims.
- Exact event dates, selection requirements, panel composition and submission rules.
- All quoted cost/time/accuracy gains.
- Insurability, legal liability and automatic compliance.
- Named historical failure stories from §14.

These claims are unnecessary for building the core system. Omit them until backed by primary evidence or real project measurements.

## Updating this source register

During P0 and P6 add:
- Exact installed SDK/library versions.
- Chosen MCP revision and tested clients.
- Exact selected component pages, licences and copied paths.
- Model provider documentation relevant to actual model/version behaviour.
- Any framework version used for evidence mapping.

When current documentation disagrees with a dossier example, record the technical update in DECISIONS.md and change the affected contract. Preserve the accepted product purpose.

