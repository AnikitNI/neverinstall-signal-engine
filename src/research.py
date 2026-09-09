import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


CUSTOMER_SIGNALS = [
    "citrix",
    "vdi",
    "azure_virtual_desktop",
    "vmware_horizon",
    "cloud_migration",
    "remote_workforce",
    "rapid_hiring",
    "compliance",
    "gpu_workloads",
]


PARTNER_SIGNALS = [
    "managed_service_provider",
    "systems_integrator",
    "cloud_consulting",
    "it_infrastructure_services",
    "vdi_services",
    "citrix_services",
    "vmware_services",
    "azure_services",
    "cloud_migration_services",
    "reseller_or_channel",
    "managed_desktop_services",
    "cloud_infrastructure_services",
]


def research_company(company):
    prompt = f"""
Research {company} as a potential enterprise customer OR partner for
Neverinstall.

The geographic region is included in the company name.

==================================================
1. IDENTITY RESOLUTION
==================================================

First determine the exact company being researched.

Verify:
- Exact company name
- Country / region
- Official website where possible
- Whether the company identity is clear

Set identity_confidence to:

"high":
The company and region are clearly identified.

"medium":
The company is probably identified correctly but some ambiguity exists.

"low":
The company name is ambiguous or the exact entity cannot be confidently
identified.

If identity_confidence is LOW:
- Do not manufacture signals.
- Return empty customer_signals and partner_signals.
- Set recommended_motion to "manual_review".
- Set bucket to "LOW_FIT".

==================================================
2. CUSTOMER RESEARCH
==================================================

Neverinstall provides secure virtual desktops and cloud workspaces.

Look for evidence that the company itself may need Neverinstall.

Customer signals:

{", ".join(CUSTOMER_SIGNALS)}

Qualification rules:

- citrix:
  Evidence that the company itself uses Citrix products such as
  Citrix Virtual Apps and Desktops, Citrix Workspace or XenApp.

- vdi:
  Evidence that the company itself operates virtual desktops,
  desktop virtualization or VDI.

- azure_virtual_desktop:
  Evidence that the company itself uses Microsoft Azure Virtual Desktop.

- vmware_horizon:
  Evidence that the company itself uses VMware Horizon.

- cloud_migration:
  Active or recent infrastructure/cloud migration that could affect
  employee computing, applications, desktops or data-center strategy.

- remote_workforce:
  Meaningful distributed/hybrid/remote workforce evidence that could
  create a need for secure centralized workspaces.

- rapid_hiring:
  Significant workforce growth or hiring expansion that could create
  workspace or infrastructure requirements.

- compliance:
  Regulatory or security requirements relevant to secure access,
  controlled environments or workspace infrastructure.

- gpu_workloads:
  Employees/users requiring GPU-enabled desktops or compute-heavy
  virtual environments.

IMPORTANT:
Technology that the company SELLS to customers is NOT customer evidence.

==================================================
3. PARTNER RESEARCH
==================================================

Look for evidence that the company could partner with Neverinstall.

Partner signals:

{", ".join(PARTNER_SIGNALS)}

Qualification rules:

- managed_service_provider:
  Provides managed IT services to customers.

- systems_integrator:
  Designs, implements or integrates enterprise IT systems.

- cloud_consulting:
  Provides cloud consulting or transformation services.

- it_infrastructure_services:
  Provides enterprise infrastructure services.

- vdi_services:
  Implements or manages VDI for customers.

- citrix_services:
  Implements, manages or consults on Citrix for customers.

- vmware_services:
  Implements, manages or consults on VMware for customers.

- azure_services:
  Provides Microsoft Azure implementation or consulting.

- cloud_migration_services:
  Performs cloud migration projects for customers.

- reseller_or_channel:
  Has reseller, distributor, referral or channel relationships.

- managed_desktop_services:
  Provides managed desktop or end-user computing services.

- cloud_infrastructure_services:
  Provides cloud infrastructure, private cloud, hybrid cloud or
  managed cloud infrastructure services.

IMPORTANT:
A company mentioning VDI, cloud, GPU or virtualization does not
automatically become a customer.

It may instead be a PARTNER.

==================================================
4. EVIDENCE STRENGTH
==================================================

For every TRUE signal classify strength:

HIGH:
Direct evidence from current company documentation, technology
documentation, official announcement or clear recent project evidence.

MEDIUM:
Credible indirect evidence such as recent job postings, partner pages,
case studies or reputable third-party reporting.

LOW:
Old, indirect, ambiguous or weak evidence.

Do not mark a signal TRUE without evidence.

==================================================
5. RECENCY
==================================================

For every TRUE signal classify:

"recent":
Approximately the last 12 months.

"old":
Clearly older than approximately 12 months.

"unknown":
Publication date cannot be confidently determined.

Do not invent dates.

==================================================
6. GTM CLASSIFICATION
==================================================

Choose exactly one:

"CUSTOMER":
The company itself appears to have a meaningful need for Neverinstall.

"PARTNER":
The company appears capable of implementing, reselling, referring
or deploying Neverinstall for customers.

"ECOSYSTEM":
Potential strategic technology/ecosystem relationship but not a clear
customer or channel partner.

"LOW_FIT":
Insufficient evidence for a meaningful opportunity.

Also provide:

customer_fit:
"high", "medium", "low"

partner_fit:
"high", "medium", "low"

==================================================
7. BUYER PERSONAS
==================================================

Identify up to 3 relevant personas to target.

For CUSTOMER accounts, prioritize roles such as:

- CIO
- CTO
- Head of Infrastructure
- Director of Infrastructure
- Head of End User Computing
- Digital Workplace Director
- Workplace Technology Lead
- EUC Lead
- Cloud Platform Director
- Cloud Infrastructure Manager
- IT Operations Director
- Information Security leadership when security/access is a major trigger

For PARTNER accounts, prioritize roles such as:

- Head of Alliances
- Director of Alliances
- Partner Director
- Channel Director
- Cloud Practice Director
- Microsoft Practice Lead
- Modern Workplace Practice Lead
- Digital Workplace Director
- Managed Services Director
- Cloud Services Director
- Solutions Director

Do NOT claim a person actually holds the role unless evidence supports it.

We want ROLE recommendations, not invented people.

Each persona must contain:

- title
- confidence
- reason

Confidence:

"high":
The role clearly owns the relevant capability.

"medium":
The role is likely relevant but ownership is uncertain.

"low":
The role is only indirectly relevant.

==================================================
8. WHY NOW
==================================================

Write a concise sales-oriented explanation of why this account could
be worth contacting now.

Use actual detected evidence.

Good:

"Existing Citrix environment plus active cloud migration creates a
potential desktop modernization trigger."

Bad:

"This company may benefit from Neverinstall."

Do not invent a trigger.

If there is no meaningful trigger:

"No strong time-sensitive trigger identified."

==================================================
9. NEVERINSTALL ANGLE
==================================================

Write one concise sentence explaining how Neverinstall should be
positioned for this specific account.

For CUSTOMER:

Focus on secure virtual desktops, workspace modernization,
cloud migration, centralized access, reducing legacy VDI complexity,
or controlled access where supported by evidence.

For PARTNER:

Focus on adding Neverinstall as a secure workspace / virtual desktop
capability to their existing services, cloud, managed workplace,
VDI or infrastructure portfolio.

Do not claim capabilities that were not established.

==================================================
10. RECOMMENDED MOTION
==================================================

Choose exactly one:

"direct_outbound"
"partner_outreach"
"ecosystem_outreach"
"manual_review"
"do_not_prioritize"

==================================================
11. SOURCES
==================================================

Prefer:

1. Official company sources
2. Official technology/vendor documentation
3. Government sources
4. Reputable publications
5. Job postings and other credible evidence

For every TRUE signal provide a source URL.

==================================================
12. OUTPUT
==================================================

Return ONLY valid JSON.

Required structure:

{{
  "company": "{company}",

  "identity": {{
    "identity_confidence": "high",
    "resolved_name": "Exact company name",
    "country": "Country",
    "official_website": "https://example.com"
  }},

  "classification": {{
    "bucket": "CUSTOMER",
    "customer_fit": "high",
    "partner_fit": "low"
  }},

  "customer_signals": [
    {{
      "signal": "citrix",
      "strength": "high",
      "recency": "recent",
      "reason": "Short explanation of evidence",
      "source": "https://example.com"
    }}
  ],

  "partner_signals": [
    {{
      "signal": "systems_integrator",
      "strength": "high",
      "recency": "recent",
      "reason": "Short explanation of evidence",
      "source": "https://example.com"
    }}
  ],

  "buyer_personas": [
    {{
      "title": "Head of End User Computing",
      "confidence": "high",
      "reason": "Owns desktop virtualization and workspace modernization."
    }}
  ],

  "why_now": "Short evidence-based sales trigger.",

  "neverinstall_angle": "Short account-specific positioning angle.",

  "recommended_motion": "direct_outbound",

  "summary": "Short explanation of the GTM opportunity."
}}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        tools=[{"type": "web_search"}],
        input=prompt
    )

    text = response.output_text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)


if __name__ == "__main__":
    result = research_company("Datacom, Australia")
    print(json.dumps(result, indent=2))