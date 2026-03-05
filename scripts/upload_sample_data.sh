#!/bin/bash
#
# Upload Sample Data for Zava Airlines
# Populates search indexes with sample airline documents
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

log_step "Uploading Sample Data for Zava Airlines"

API_VERSION="2024-11-01-preview"

upload_docs() {
    local index=$1
    local payload=$2
    
    log_info "Uploading documents to: $index"
    
    HTTP_CODE=$(curl -s -o /tmp/upload_response.json -w "%{http_code}" \
        -X POST "${SEARCH_ENDPOINT}/indexes/${index}/docs/index?api-version=${API_VERSION}" \
        -H "api-key: ${SEARCH_KEY}" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
        log_success "Uploaded documents to: $index"
    else
        log_warn "Upload to $index may have issues (HTTP $HTTP_CODE)"
    fi
}

# --- Customer Service Documents ---
log_step "Customer Service Documents"

upload_docs "index-customer-service" '{
    "value": [
        {
            "@search.action": "upload",
            "id": "cs-001",
            "title": "Flight Rebooking Policy",
            "content": "Zava Airlines Rebooking Policy: Passengers may rebook flights up to 24 hours before departure with no change fee for Flex and Business fares. Economy Basic fares incur a $75 change fee. In case of airline-initiated schedule changes, irregular operations, or geo-political disruptions (airspace closures, travel bans), all passengers are eligible for free rebooking to the next available flight or a full refund. Rebooking can be done via the Zava Airlines app, website, or by contacting our customer service center at 1-800-ZAVA-FLY.",
            "category": "rebooking",
            "policy_type": "passenger-rights"
        },
        {
            "@search.action": "upload",
            "id": "cs-002",
            "title": "Refund and Compensation Guidelines",
            "content": "Zava Airlines Refund Policy: Full refunds are available for cancellations made within 24 hours of booking (DOT 24-hour rule). For EU routes, EU261/2004 applies: compensation of €250-€600 based on distance for delays over 3 hours, cancellations without 14-day notice, or denied boarding. Compensation is not payable for extraordinary circumstances including severe weather, air traffic control restrictions, geo-political events, or security threats. Refunds are processed to the original payment method within 7 business days for credit cards and 20 business days for other methods.",
            "category": "refunds",
            "policy_type": "compensation"
        },
        {
            "@search.action": "upload",
            "id": "cs-003",
            "title": "Baggage Policy",
            "content": "Zava Airlines Baggage Allowance: Economy - 1 checked bag (23kg), Business - 2 checked bags (32kg each), First - 3 checked bags (32kg each). Carry-on: 1 bag (10kg, 55x40x20cm) + 1 personal item for all classes. Excess baggage fee: $50 per additional bag, $100 for overweight (23-32kg). Lost baggage: File a report within 21 days. Zava Airlines compensates up to $3,800 per passenger for international flights (Montreal Convention). Delayed baggage: Reasonable expenses reimbursed up to $200/day for essentials.",
            "category": "baggage",
            "policy_type": "service"
        },
        {
            "@search.action": "upload",
            "id": "cs-004",
            "title": "Seat Upgrade Policy",
            "content": "Zava Airlines Seat Upgrade Options: 1) Bid Upgrade: Place a bid for Business/First class starting 72 hours before departure. 2) Miles Upgrade: Use SkyRewards miles - Economy to Business: 15,000-40,000 miles depending on route. Business to First: 20,000-50,000 miles. 3) Cash Upgrade: Available at check-in kiosks and gates, pricing is dynamic. 4) Complimentary Upgrade: Offered to SkyRewards Gold and above members when available, priority based on tier status. Diamond members receive confirmed upgrades 24 hours before departure when space permits.",
            "category": "upgrades",
            "policy_type": "service"
        },
        {
            "@search.action": "upload",
            "id": "cs-005",
            "title": "Geo-Political Disruption Customer Policy",
            "content": "Zava Airlines Geo-Political Disruption Policy: When flights are disrupted due to geo-political events (armed conflicts, airspace closures, government travel bans, sanctions), Zava Airlines offers: 1) Free rebooking to alternative routes. 2) Full refund if no suitable alternative exists. 3) Hotel and meal vouchers for stranded passengers. 4) Priority re-routing for unaccompanied minors, medical needs, and elderly passengers. 5) Real-time SMS/email updates on route status. Customers should monitor the Zava Airlines app Travel Advisory section for the latest information.",
            "category": "disruptions",
            "policy_type": "passenger-rights"
        }
    ]
}'

# --- Operations Documents ---
log_step "Operations Documents"

upload_docs "index-operations" '{
    "value": [
        {
            "@search.action": "upload",
            "id": "ops-001",
            "title": "Flight Operations Manual - Disruption Management",
            "content": "Zava Airlines Disruption Management Playbook: Level 1 (Minor): Delays under 2 hrs, handle at gate level. Level 2 (Moderate): Delays 2-6 hrs or single flight cancellation, activate crew standby pool, offer meal vouchers. Level 3 (Major): Multiple cancellations or hub disruption, activate Emergency Operations Center (EOC), deploy recovery flights. Level 4 (Critical): Network-wide disruption due to weather, geo-political event, or airspace closure - activate full Irregular Operations (IROPS) plan, engage all partner airlines for passenger re-accommodation, open 24/7 customer service overflow.",
            "category": "disruption-management",
            "region": "global",
            "severity": "all"
        },
        {
            "@search.action": "upload",
            "id": "ops-002",
            "title": "Airspace Advisory - Eastern Europe and Middle East",
            "content": "NOTAM Advisory: Due to ongoing geo-political tensions, the following airspace restrictions apply to Zava Airlines operations: Ukraine (UKXX) - CLOSED to civil aviation. Belarus (UMXX) - EU carrier overfly prohibited. Parts of Iraq (ORBB FIR above FL250 open), Syria (OSTT) - CLOSED. Iran-Iraq border area - exercise caution. All Zava Airlines flights use approved alternate routing: Europe-Gulf via Turkey/Egypt corridor. Europe-Asia via Kazakhstan/Uzbekistan corridor. Additional fuel loading required for detour routes, approximately 15-45 minutes additional flight time depending on city pair.",
            "category": "airspace-advisory",
            "region": "eastern-europe-middle-east",
            "severity": "critical"
        },
        {
            "@search.action": "upload",
            "id": "ops-003",
            "title": "Crew Management and Duty Time Rules",
            "content": "Zava Airlines Crew Duty Regulations: Maximum Flight Duty Period (FDP): 13 hours for 2-pilot crew, 17 hours with augmented crew (3 pilots). Minimum rest between duties: 12 hours including 8 hours sleep opportunity. Annual flight time limit: 1,000 hours. Fatigue Risk Management: Pilots must report fatigue using the ZA-FR8 form. Crew scheduling must maintain minimum 2 days off per 7-day period. For geo-political rerouting, duty time extensions of up to 2 hours are permitted under Commander discretion with mandatory fatigue report filing.",
            "category": "crew-management",
            "region": "global",
            "severity": "standard"
        },
        {
            "@search.action": "upload",
            "id": "ops-004",
            "title": "Route Network and Scheduling",
            "content": "Zava Airlines Route Network: Hub airports - London Heathrow (LHR), Dubai (DXB), Singapore Changi (SIN). Focus cities - New York JFK, Frankfurt FRA, Tokyo NRT, Sydney SYD. Total fleet: 85 aircraft (A320neo, A350-900, B787-9). Network serves 120 destinations across 45 countries. Average daily departures: 450. On-time performance target: 85%. Load factor target: 82%. Key long-haul routes: LHR-DXB (8x daily), LHR-SIN (3x daily), LHR-JFK (6x daily), DXB-SIN (4x daily). Seasonal routes adjusted quarterly based on demand and geo-political conditions.",
            "category": "network",
            "region": "global",
            "severity": "standard"
        },
        {
            "@search.action": "upload",
            "id": "ops-005",
            "title": "Geo-Political Risk Assessment Framework",
            "content": "Zava Airlines Geo-Political Risk Framework: Risk levels - GREEN (normal ops), AMBER (enhanced monitoring), RED (route suspension). Assessment criteria: 1) Active armed conflict in operating area, 2) Government travel advisory level, 3) Insurance coverage availability, 4) Diplomatic relations status, 5) NOTAM/airspace status. Current RED zones: Ukraine, Syria, Libya. Current AMBER zones: Iran overfly, Red Sea corridor (Houthi threat), Ethiopia-Eritrea border. Risk Committee meets weekly or ad-hoc for emerging situations. All risk assessments integrate with Bing Search real-time intelligence for breaking geo-political developments.",
            "category": "geo-political",
            "region": "global",
            "severity": "critical"
        }
    ]
}'

# --- Loyalty Documents ---
log_step "Loyalty Documents"

upload_docs "index-loyalty" '{
    "value": [
        {
            "@search.action": "upload",
            "id": "loy-001",
            "title": "SkyRewards Program Overview",
            "content": "Zava Airlines SkyRewards Frequent Flyer Program: Tiers - Blue (entry), Silver (25K miles/year), Gold (50K miles/year), Platinum (75K miles/year), Diamond (100K miles/year). Miles earning: Economy 1x base miles, Premium Economy 1.5x, Business 2x, First 3x. Miles are valid for 36 months from earning date. SkyRewards miles can be earned on Zava Airlines and all Star Alliance partner flights. Family pooling available for up to 6 members sharing one account. Miles transfer between members: 1,000 mile minimum, no fee for Gold and above.",
            "category": "program-overview",
            "tier": "all"
        },
        {
            "@search.action": "upload",
            "id": "loy-002",
            "title": "Tier Benefits Comparison",
            "content": "SkyRewards Tier Benefits: BLUE - earn miles, basic perks. SILVER - priority check-in, 1 extra bag (23kg), economy seat selection, 25% bonus miles. GOLD - lounge access (Zava + Star Alliance), priority boarding, 2 extra bags, upgrade waitlist priority, 50% bonus miles, complimentary seat selection all classes. PLATINUM - premium lounge access, guaranteed upgrades (72hr advance), 3 extra bags, dedicated phone line, 75% bonus miles, chauffeur service in hub cities. DIAMOND - all Platinum + First Class lounge access, confirmed upgrades 24hr advance, unlimited bags, personal travel coordinator, 100% bonus miles, guaranteed availability.",
            "category": "tier-benefits",
            "tier": "all"
        },
        {
            "@search.action": "upload",
            "id": "loy-003",
            "title": "Miles Redemption Guide",
            "content": "SkyRewards Miles Redemption: Award flights - Short-haul Economy: 10,000 miles, Business: 25,000 miles. Medium-haul Economy: 25,000 miles, Business: 50,000 miles. Long-haul Economy: 40,000 miles, Business: 80,000 miles, First: 120,000 miles. Upgrade awards: Economy to Business short-haul 15,000 miles, long-haul 40,000 miles. Non-flight redemptions: Hotel stays from 5,000 miles/night, car rental from 3,000 miles/day, gift cards from 2,500 miles. Star Alliance partner awards available at slightly higher rates. Taxes and surcharges apply to all award bookings.",
            "category": "redemption",
            "tier": "all",
            "miles_value": 10000
        },
        {
            "@search.action": "upload",
            "id": "loy-004",
            "title": "Lounge Access Rules",
            "content": "Zava Airlines Lounge Access: SkyRewards Gold+ members: complimentary access to Zava Lounges worldwide and Star Alliance lounges. Zava Premium Lounges (LHR, DXB, SIN): Platinum+ members or Business/First passengers. Day pass available for purchase: $60 per visit. Guest policy: Gold - no guests, Platinum - 1 guest, Diamond - 2 guests. Lounge features: hot/cold buffet, premium bar, shower suites (premium lounges), business center, WiFi, rest areas. Priority Pass and LoungeKey accepted at select locations. Children under 12 enter free with qualifying member.",
            "category": "lounge-access",
            "tier": "gold"
        },
        {
            "@search.action": "upload",
            "id": "loy-005",
            "title": "Partner Airlines and Status Match",
            "content": "SkyRewards Partner Network: As a Star Alliance member, earn and redeem miles on 26 member airlines. Key partners: Lufthansa, United Airlines, ANA, Singapore Airlines, Air Canada, Turkish Airlines. Earning rates on partners: 50-100% of base miles depending on fare class. Status match program: Zava Airlines offers a 90-day status match challenge for qualifying members of competing airline programs. Provide proof of status, receive temporary matched tier, earn 50% of qualification miles within 90 days to retain status. Non-alliance partners: Emirates (codeshare select routes), JetBlue (interline), Etihad (reciprocal lounge).",
            "category": "partners",
            "tier": "all"
        }
    ]
}'

log_success "All sample data uploaded successfully!"
