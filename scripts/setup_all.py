"""
Zava Airlines - Complete Setup Script (Windows-friendly)

Creates indexes, uploads sample data, creates knowledge sources and knowledge bases.
Run with: python scripts/setup_all.py
"""

import json
import os
import sys
import time
import requests

# ── Configuration ──────────────────────────────────────────────────────
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://<your-search-service>.search.windows.net")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY", "")  # Will prompt if empty
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://<your-ai-resource>.cognitiveservices.azure.com/")
MODEL_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")

INDEX_API_VERSION = "2024-11-01-preview"
KB_API_VERSION = "2025-11-01-preview"

def get_headers():
    return {
        "api-key": SEARCH_KEY,
        "Content-Type": "application/json",
    }

def log_step(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")

def log_ok(msg):
    print(f"  [OK] {msg}")

def log_warn(msg):
    print(f"  [WARN] {msg}")

def log_info(msg):
    print(f"  [INFO] {msg}")

# ── Step 1: Create Search Indexes ──────────────────────────────────────

INDEXES = {
    "index-customer-service": {
        "name": "index-customer-service",
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "title", "type": "Edm.String", "searchable": True, "filterable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "category", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "policy_type", "type": "Edm.String", "filterable": True},
            {"name": "last_updated", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True},
            {
                "name": "content_vector",
                "type": "Collection(Edm.Single)",
                "searchable": True,
                "dimensions": 3072,
                "vectorSearchProfile": "default-profile",
            },
        ],
        "vectorSearch": {
            "algorithms": [{"name": "default-algo", "kind": "hnsw"}],
            "profiles": [{"name": "default-profile", "algorithm": "default-algo"}],
        },
    },
    "index-operations": {
        "name": "index-operations",
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "title", "type": "Edm.String", "searchable": True, "filterable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "category", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "region", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "severity", "type": "Edm.String", "filterable": True},
            {"name": "effective_date", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True},
            {
                "name": "content_vector",
                "type": "Collection(Edm.Single)",
                "searchable": True,
                "dimensions": 3072,
                "vectorSearchProfile": "default-profile",
            },
        ],
        "vectorSearch": {
            "algorithms": [{"name": "default-algo", "kind": "hnsw"}],
            "profiles": [{"name": "default-profile", "algorithm": "default-algo"}],
        },
    },
    "index-loyalty": {
        "name": "index-loyalty",
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "title", "type": "Edm.String", "searchable": True, "filterable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "category", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "tier", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "miles_value", "type": "Edm.Int32", "filterable": True, "sortable": True},
            {
                "name": "content_vector",
                "type": "Collection(Edm.Single)",
                "searchable": True,
                "dimensions": 3072,
                "vectorSearchProfile": "default-profile",
            },
        ],
        "vectorSearch": {
            "algorithms": [{"name": "default-algo", "kind": "hnsw"}],
            "profiles": [{"name": "default-profile", "algorithm": "default-algo"}],
        },
    },
}

def create_indexes():
    log_step("Step 1: Creating Search Indexes")
    for name, schema in INDEXES.items():
        url = f"{SEARCH_ENDPOINT}/indexes/{name}?api-version={INDEX_API_VERSION}"
        resp = requests.put(url, headers=get_headers(), json=schema)
        if resp.status_code in (200, 201, 204):
            log_ok(f"Created index: {name}")
        elif resp.status_code == 400 and "already exists" in resp.text.lower():
            log_warn(f"Index {name} already exists, skipping")
        else:
            log_warn(f"Index {name}: HTTP {resp.status_code} - {resp.text[:200]}")

# ── Step 2: Upload Sample Documents ───────────────────────────────────

CUSTOMER_SERVICE_DOCS = [
    {
        "@search.action": "upload",
        "id": "cs-001",
        "title": "Flight Rebooking Policy",
        "content": "Zava Airlines Rebooking Policy: Passengers may rebook flights up to 24 hours before departure with no change fee for Flex and Business fares. Economy Basic fares incur a $75 change fee. In case of airline-initiated schedule changes, irregular operations, or geo-political disruptions (airspace closures, travel bans), all passengers are eligible for free rebooking to the next available flight or a full refund. Rebooking can be done via the Zava Airlines app, website, or by contacting our customer service center at 1-800-ZAVA-FLY.",
        "category": "rebooking",
        "policy_type": "passenger-rights",
    },
    {
        "@search.action": "upload",
        "id": "cs-002",
        "title": "Refund and Compensation Guidelines",
        "content": "Zava Airlines Refund Policy: Full refunds are available for cancellations made within 24 hours of booking (DOT 24-hour rule). For EU routes, EU261/2004 applies: compensation of \u20ac250-\u20ac600 based on distance for delays over 3 hours, cancellations without 14-day notice, or denied boarding. Compensation is not payable for extraordinary circumstances including severe weather, air traffic control restrictions, geo-political events, or security threats. Refunds are processed to the original payment method within 7 business days for credit cards and 20 business days for other methods.",
        "category": "refunds",
        "policy_type": "compensation",
    },
    {
        "@search.action": "upload",
        "id": "cs-003",
        "title": "Baggage Policy",
        "content": "Zava Airlines Baggage Allowance: Economy - 1 checked bag (23kg), Business - 2 checked bags (32kg each), First - 3 checked bags (32kg each). Carry-on: 1 bag (10kg, 55x40x20cm) + 1 personal item for all classes. Excess baggage fee: $50 per additional bag, $100 for overweight (23-32kg). Lost baggage: File a report within 21 days. Zava Airlines compensates up to $3,800 per passenger for international flights (Montreal Convention). Delayed baggage: Reasonable expenses reimbursed up to $200/day for essentials.",
        "category": "baggage",
        "policy_type": "service",
    },
    {
        "@search.action": "upload",
        "id": "cs-004",
        "title": "Seat Upgrade Policy",
        "content": "Zava Airlines Seat Upgrade Options: 1) Bid Upgrade: Place a bid for Business/First class starting 72 hours before departure. 2) Miles Upgrade: Use SkyRewards miles - Economy to Business: 15,000-40,000 miles depending on route. Business to First: 20,000-50,000 miles. 3) Cash Upgrade: Available at check-in kiosks and gates, pricing is dynamic. 4) Complimentary Upgrade: Offered to SkyRewards Gold and above members when available, priority based on tier status. Diamond members receive confirmed upgrades 24 hours before departure when space permits.",
        "category": "upgrades",
        "policy_type": "service",
    },
    {
        "@search.action": "upload",
        "id": "cs-005",
        "title": "Geo-Political Disruption Customer Policy",
        "content": "Zava Airlines Geo-Political Disruption Policy: When flights are disrupted due to geo-political events (armed conflicts, airspace closures, government travel bans, sanctions), Zava Airlines offers: 1) Free rebooking to alternative routes. 2) Full refund if no suitable alternative exists. 3) Hotel and meal vouchers for stranded passengers. 4) Priority re-routing for unaccompanied minors, medical needs, and elderly passengers. 5) Real-time SMS/email updates on route status. Customers should monitor the Zava Airlines app Travel Advisory section for the latest information.",
        "category": "disruptions",
        "policy_type": "passenger-rights",
    },
]

OPERATIONS_DOCS = [
    {
        "@search.action": "upload",
        "id": "ops-001",
        "title": "Flight Operations Manual - Disruption Management",
        "content": "Zava Airlines Disruption Management Playbook: Level 1 (Minor): Delays under 2 hrs, handle at gate level. Level 2 (Moderate): Delays 2-6 hrs or single flight cancellation, activate crew standby pool, offer meal vouchers. Level 3 (Major): Multiple cancellations or hub disruption, activate Emergency Operations Center (EOC), deploy recovery flights. Level 4 (Critical): Network-wide disruption due to weather, geo-political event, or airspace closure - activate full Irregular Operations (IROPS) plan, engage all partner airlines for passenger re-accommodation, open 24/7 customer service overflow.",
        "category": "disruption-management",
        "region": "global",
        "severity": "all",
    },
    {
        "@search.action": "upload",
        "id": "ops-002",
        "title": "Airspace Advisory - Eastern Europe and Middle East",
        "content": "NOTAM Advisory: Due to ongoing geo-political tensions, the following airspace restrictions apply to Zava Airlines operations: Ukraine (UKXX) - CLOSED to civil aviation. Belarus (UMXX) - EU carrier overfly prohibited. Parts of Iraq (ORBB FIR above FL250 open), Syria (OSTT) - CLOSED. Iran-Iraq border area - exercise caution. All Zava Airlines flights use approved alternate routing: Europe-Gulf via Turkey/Egypt corridor. Europe-Asia via Kazakhstan/Uzbekistan corridor. Additional fuel loading required for detour routes, approximately 15-45 minutes additional flight time depending on city pair.",
        "category": "airspace-advisory",
        "region": "eastern-europe-middle-east",
        "severity": "critical",
    },
    {
        "@search.action": "upload",
        "id": "ops-003",
        "title": "Crew Management and Duty Time Rules",
        "content": "Zava Airlines Crew Duty Regulations: Maximum Flight Duty Period (FDP): 13 hours for 2-pilot crew, 17 hours with augmented crew (3 pilots). Minimum rest between duties: 12 hours including 8 hours sleep opportunity. Annual flight time limit: 1,000 hours. Fatigue Risk Management: Pilots must report fatigue using the ZA-FR8 form. Crew scheduling must maintain minimum 2 days off per 7-day period. For geo-political rerouting, duty time extensions of up to 2 hours are permitted under Commander discretion with mandatory fatigue report filing.",
        "category": "crew-management",
        "region": "global",
        "severity": "standard",
    },
    {
        "@search.action": "upload",
        "id": "ops-004",
        "title": "Route Network and Scheduling",
        "content": "Zava Airlines Route Network: Hub airports - London Heathrow (LHR), Dubai (DXB), Singapore Changi (SIN). Focus cities - New York JFK, Frankfurt FRA, Tokyo NRT, Sydney SYD. Total fleet: 85 aircraft (A320neo, A350-900, B787-9). Network serves 120 destinations across 45 countries. Average daily departures: 450. On-time performance target: 85%. Load factor target: 82%. Key long-haul routes: LHR-DXB (8x daily), LHR-SIN (3x daily), LHR-JFK (6x daily), DXB-SIN (4x daily). Seasonal routes adjusted quarterly based on demand and geo-political conditions.",
        "category": "network",
        "region": "global",
        "severity": "standard",
    },
    {
        "@search.action": "upload",
        "id": "ops-005",
        "title": "Geo-Political Risk Assessment Framework",
        "content": "Zava Airlines Geo-Political Risk Framework: Risk levels - GREEN (normal ops), AMBER (enhanced monitoring), RED (route suspension). Assessment criteria: 1) Active armed conflict in operating area, 2) Government travel advisory level, 3) Insurance coverage availability, 4) Diplomatic relations status, 5) NOTAM/airspace status. Current RED zones: Ukraine, Syria, Libya. Current AMBER zones: Iran overfly, Red Sea corridor (Houthi threat), Ethiopia-Eritrea border. Risk Committee meets weekly or ad-hoc for emerging situations. All risk assessments integrate with Bing Search real-time intelligence for breaking geo-political developments.",
        "category": "geo-political",
        "region": "global",
        "severity": "critical",
    },
]

LOYALTY_DOCS = [
    {
        "@search.action": "upload",
        "id": "loy-001",
        "title": "SkyRewards Program Overview",
        "content": "Zava Airlines SkyRewards Frequent Flyer Program: Tiers - Blue (entry), Silver (25K miles/year), Gold (50K miles/year), Platinum (75K miles/year), Diamond (100K miles/year). Miles earning: Economy 1x base miles, Premium Economy 1.5x, Business 2x, First 3x. Miles are valid for 36 months from earning date. SkyRewards miles can be earned on Zava Airlines and all Star Alliance partner flights. Family pooling available for up to 6 members sharing one account. Miles transfer between members: 1,000 mile minimum, no fee for Gold and above.",
        "category": "program-overview",
        "tier": "all",
    },
    {
        "@search.action": "upload",
        "id": "loy-002",
        "title": "Tier Benefits Comparison",
        "content": "SkyRewards Tier Benefits: BLUE - earn miles, basic perks. SILVER - priority check-in, 1 extra bag (23kg), economy seat selection, 25% bonus miles. GOLD - lounge access (Zava + Star Alliance), priority boarding, 2 extra bags, upgrade waitlist priority, 50% bonus miles, complimentary seat selection all classes. PLATINUM - premium lounge access, guaranteed upgrades (72hr advance), 3 extra bags, dedicated phone line, 75% bonus miles, chauffeur service in hub cities. DIAMOND - all Platinum + First Class lounge access, confirmed upgrades 24hr advance, unlimited bags, personal travel coordinator, 100% bonus miles, guaranteed availability.",
        "category": "tier-benefits",
        "tier": "all",
    },
    {
        "@search.action": "upload",
        "id": "loy-003",
        "title": "Miles Redemption Guide",
        "content": "SkyRewards Miles Redemption: Award flights - Short-haul Economy: 10,000 miles, Business: 25,000 miles. Medium-haul Economy: 25,000 miles, Business: 50,000 miles. Long-haul Economy: 40,000 miles, Business: 80,000 miles, First: 120,000 miles. Upgrade awards: Economy to Business short-haul 15,000 miles, long-haul 40,000 miles. Non-flight redemptions: Hotel stays from 5,000 miles/night, car rental from 3,000 miles/day, gift cards from 2,500 miles. Star Alliance partner awards available at slightly higher rates. Taxes and surcharges apply to all award bookings.",
        "category": "redemption",
        "tier": "all",
        "miles_value": 10000,
    },
    {
        "@search.action": "upload",
        "id": "loy-004",
        "title": "Lounge Access Rules",
        "content": "Zava Airlines Lounge Access: SkyRewards Gold+ members: complimentary access to Zava Lounges worldwide and Star Alliance lounges. Zava Premium Lounges (LHR, DXB, SIN): Platinum+ members or Business/First passengers. Day pass available for purchase: $60 per visit. Guest policy: Gold - no guests, Platinum - 1 guest, Diamond - 2 guests. Lounge features: hot/cold buffet, premium bar, shower suites (premium lounges), business center, WiFi, rest areas. Priority Pass and LoungeKey accepted at select locations. Children under 12 enter free with qualifying member.",
        "category": "lounge-access",
        "tier": "gold",
    },
    {
        "@search.action": "upload",
        "id": "loy-005",
        "title": "Partner Airlines and Status Match",
        "content": "SkyRewards Partner Network: As a Star Alliance member, earn and redeem miles on 26 member airlines. Key partners: Lufthansa, United Airlines, ANA, Singapore Airlines, Air Canada, Turkish Airlines. Earning rates on partners: 50-100% of base miles depending on fare class. Status match program: Zava Airlines offers a 90-day status match challenge for qualifying members of competing airline programs. Provide proof of status, receive temporary matched tier, earn 50% of qualification miles within 90 days to retain status. Non-alliance partners: Emirates (codeshare select routes), JetBlue (interline), Etihad (reciprocal lounge).",
        "category": "partners",
        "tier": "all",
    },
]


def upload_documents():
    log_step("Step 2: Uploading Sample Documents (15 docs across 3 indexes)")

    datasets = {
        "index-customer-service": CUSTOMER_SERVICE_DOCS,
        "index-operations": OPERATIONS_DOCS,
        "index-loyalty": LOYALTY_DOCS,
    }

    for index_name, docs in datasets.items():
        url = f"{SEARCH_ENDPOINT}/indexes/{index_name}/docs/index?api-version={INDEX_API_VERSION}"
        payload = {"value": docs}
        resp = requests.post(url, headers=get_headers(), json=payload)
        if resp.status_code in (200, 201, 207):
            log_ok(f"Uploaded {len(docs)} docs to {index_name}")
        else:
            log_warn(f"Upload to {index_name}: HTTP {resp.status_code} - {resp.text[:300]}")

    # Give indexer a moment
    log_info("Waiting 3s for index refresh...")
    time.sleep(3)

# ── Step 3: Create Knowledge Sources ──────────────────────────────────

KNOWLEDGE_SOURCES = [
    # Customer Service
    {
        "name": "ks-cs-aisearch",
        "type": "searchIndex",
        "searchIndexParameters": {"indexName": "index-customer-service"},
    },
    {
        "name": "ks-cs-web",
        "type": "web",
        "webParameters": {
            "urls": [
                "https://www.iata.org/en/programs/ops-infra/baggage/",
                "https://www.transportation.gov/airconsumer",
                "https://europa.eu/youreurope/citizens/travel/passenger-rights/air/index_en.htm",
            ]
        },
    },
    {
        "name": "ks-cs-sharepoint",
        "type": "searchIndex",
        "searchIndexParameters": {"indexName": "index-customer-service"},
    },
    # Operations
    {
        "name": "ks-ops-aisearch",
        "type": "searchIndex",
        "searchIndexParameters": {"indexName": "index-operations"},
    },
    {
        "name": "ks-ops-web",
        "type": "web",
        "webParameters": {
            "urls": [
                "https://www.faa.gov/air_traffic/publications/notams",
                "https://www.eurocontrol.int/",
                "https://www.icao.int/safety/Pages/default.aspx",
            ]
        },
    },
    {
        "name": "ks-geopolitical-bing",
        "type": "web",
        "webParameters": {
            "urls": [
                "https://www.bbc.com/news/world",
                "https://www.reuters.com/world/",
                "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html/",
                "https://www.gov.uk/foreign-travel-advice",
                "https://www.flightradar24.com",
                "https://www.eurocontrol.int/news",
            ]
        },
    },
    # Loyalty
    {
        "name": "ks-loyalty-aisearch",
        "type": "searchIndex",
        "searchIndexParameters": {"indexName": "index-loyalty"},
    },
    {
        "name": "ks-loyalty-web",
        "type": "web",
        "webParameters": {
            "urls": [
                "https://www.staralliance.com/en/member-airlines",
                "https://www.prioritypass.com/",
            ]
        },
    },
]

def create_knowledge_sources():
    log_step("Step 3: Creating Knowledge Sources (8 sources)")
    for ks in KNOWLEDGE_SOURCES:
        name = ks["name"]
        url = f"{SEARCH_ENDPOINT}/knowledgesources/{name}?api-version={KB_API_VERSION}"
        resp = requests.put(url, headers=get_headers(), json=ks)
        if resp.status_code in (200, 201, 204):
            log_ok(f"Created knowledge source: {name}")
        else:
            log_warn(f"KS {name}: HTTP {resp.status_code} - {resp.text[:300]}")

# ── Step 4: Create Knowledge Bases ────────────────────────────────────

KNOWLEDGE_BASES = [
    {
        "name": "kb1-customer-service",
        "description": "Customer service knowledge base for Zava Airlines - rebooking, refunds, complaints, baggage, and passenger assistance",
        "retrievalInstructions": "Search for airline customer service policies, rebooking procedures, refund guidelines, baggage rules, EU261/DOT compensation, seat upgrade policies, and special assistance requirements.",
        "answerInstructions": "Provide empathetic, solution-oriented answers about Zava Airlines customer service policies. Always cite the specific policy document. Offer concrete next steps and booking reference guidance. If a situation involves geo-political disruption, recommend checking with the Operations team for the latest route status.",
        "outputMode": "answerSynthesis",
        "knowledgeSources": [
            {"name": "ks-cs-aisearch"},
            {"name": "ks-cs-web"},
            {"name": "ks-cs-sharepoint"},
        ],
        "models": [
            {
                "kind": "azureOpenAI",
                "azureOpenAIParameters": {
                    "resourceUri": OPENAI_ENDPOINT,
                    "deploymentId": MODEL_NAME,
                    "modelName": MODEL_NAME,
                },
            }
        ],
        "retrievalReasoningEffort": {"kind": "medium"},
    },
    {
        "name": "kb2-operations",
        "description": "Operations knowledge base for Zava Airlines - flight ops, disruptions, crew management, and real-time geo-political intelligence via Bing Search",
        "retrievalInstructions": "Search for flight operations data, disruption management procedures, crew scheduling rules, NOTAM information, airspace closures, and geo-political situations affecting airline routes. Use the Bing Search knowledge source for the latest real-time geo-political intelligence including conflict zones, sanctions, travel bans, and airspace restrictions.",
        "answerInstructions": "Provide operational insights using IATA codes and aviation terminology. Reference real-time geo-political intelligence from Bing Search when relevant. Include severity assessments for disruptions. Always prioritize safety recommendations. Quantify passenger impact when discussing disruptions.",
        "outputMode": "answerSynthesis",
        "knowledgeSources": [
            {"name": "ks-ops-aisearch"},
            {"name": "ks-ops-web"},
            {"name": "ks-geopolitical-bing"},
        ],
        "models": [
            {
                "kind": "azureOpenAI",
                "azureOpenAIParameters": {
                    "resourceUri": OPENAI_ENDPOINT,
                    "deploymentId": MODEL_NAME,
                    "modelName": MODEL_NAME,
                },
            }
        ],
        "retrievalReasoningEffort": {"kind": "high"},
    },
    {
        "name": "kb3-loyalty",
        "description": "Loyalty program knowledge base for Zava Airlines SkyRewards - miles, tiers, lounge access, partner benefits, and redemption options",
        "retrievalInstructions": "Search for SkyRewards frequent flyer program details, tier qualification criteria, miles earning and redemption rates, lounge access rules, partner airline benefits, and promotional offers.",
        "answerInstructions": "Provide enthusiastic, detailed answers about the SkyRewards program. Reference exact mile amounts and tier thresholds. Suggest strategies to maximize miles earning and tier progression. Highlight current promotions when relevant.",
        "outputMode": "answerSynthesis",
        "knowledgeSources": [
            {"name": "ks-loyalty-aisearch"},
            {"name": "ks-loyalty-web"},
        ],
        "models": [
            {
                "kind": "azureOpenAI",
                "azureOpenAIParameters": {
                    "resourceUri": OPENAI_ENDPOINT,
                    "deploymentId": MODEL_NAME,
                    "modelName": MODEL_NAME,
                },
            }
        ],
        "retrievalReasoningEffort": {"kind": "medium"},
    },
]

def create_knowledge_bases():
    log_step("Step 4: Creating Knowledge Bases (3 KBs)")
    for kb in KNOWLEDGE_BASES:
        name = kb["name"]
        url = f"{SEARCH_ENDPOINT}/knowledgebases/{name}?api-version={KB_API_VERSION}"
        resp = requests.put(url, headers=get_headers(), json=kb)
        if resp.status_code in (200, 201, 204):
            log_ok(f"Created knowledge base: {name}")
        else:
            log_warn(f"KB {name}: HTTP {resp.status_code} - {resp.text[:500]}")

# ── Step 5: Verify ────────────────────────────────────────────────────

def verify_setup():
    log_step("Step 5: Verifying Setup")

    # Check indexes
    for idx in ["index-customer-service", "index-operations", "index-loyalty"]:
        url = f"{SEARCH_ENDPOINT}/indexes/{idx}/docs/$count?api-version={INDEX_API_VERSION}"
        resp = requests.get(url, headers=get_headers())
        if resp.status_code == 200:
            log_ok(f"{idx}: {resp.text.strip()} documents")
        else:
            log_warn(f"{idx}: could not verify ({resp.status_code})")

    # Check knowledge bases
    for kb in ["kb1-customer-service", "kb2-operations", "kb3-loyalty"]:
        url = f"{SEARCH_ENDPOINT}/knowledgebases/{kb}?api-version={KB_API_VERSION}"
        resp = requests.get(url, headers=get_headers())
        if resp.status_code == 200:
            log_ok(f"{kb}: exists")
        else:
            log_warn(f"{kb}: not found ({resp.status_code})")

# ── Main ──────────────────────────────────────────────────────────────

def main():
    global SEARCH_KEY

    print("\n" + "=" * 60)
    print("  Zava Airlines - Complete Azure Setup")
    print("=" * 60)
    print(f"\n  Search Endpoint: {SEARCH_ENDPOINT}")
    print(f"  OpenAI Endpoint: {OPENAI_ENDPOINT}")
    print(f"  Model:           {MODEL_NAME}")

    if not SEARCH_KEY:
        SEARCH_KEY = input("\n  Enter your Azure AI Search Admin API Key: ").strip()
        if not SEARCH_KEY:
            print("  ERROR: API Key is required. Find it in Azure Portal > Search > Keys")
            sys.exit(1)

    print()

    try:
        create_indexes()
        upload_documents()
        create_knowledge_sources()
        create_knowledge_bases()
        verify_setup()
    except requests.exceptions.ConnectionError as e:
        print(f"\n  ERROR: Could not connect to {SEARCH_ENDPOINT}")
        print(f"  Check that the endpoint is correct and accessible.")
        sys.exit(1)

    log_step("Setup Complete!")
    print("  Next steps:")
    print("  1. In Azure Portal: Search service > Keys > Set to 'Both' (API keys + RBAC)")
    print("  2. Run: python app/backend/agents/orchestrator.py")
    print("  3. Or start the web app: uvicorn app.backend.main:app --reload")
    print()

if __name__ == "__main__":
    main()