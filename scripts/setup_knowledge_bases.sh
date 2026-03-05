#!/bin/bash
#
# Setup Knowledge Bases for Zava Airlines
# Creates FoundryIQ knowledge bases that aggregate multiple knowledge sources
# including Bing Search for geo-political intelligence
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

log_step "Creating Knowledge Bases for Zava Airlines"

API_VERSION="2025-11-01-preview"

create_kb() {
    local name=$1
    local payload=$2
    
    log_info "Creating knowledge base: $name"
    
    HTTP_CODE=$(curl -s -o /tmp/kb_response.json -w "%{http_code}" \
        -X PUT "${SEARCH_ENDPOINT}/knowledgebases/${name}?api-version=${API_VERSION}" \
        -H "api-key: ${SEARCH_KEY}" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
        log_success "Created knowledge base: $name"
    else
        log_warn "KB $name may already exist or error (HTTP $HTTP_CODE)"
        if [ "$VERBOSE" = true ]; then
            cat /tmp/kb_response.json
        fi
    fi
}

# Get OpenAI endpoint if not set
if [ -z "$OPENAI_ENDPOINT" ]; then
    log_warn "OPENAI_ENDPOINT not set, will use placeholder"
    OPENAI_ENDPOINT="https://your-openai.openai.azure.com"
fi

# 1. Customer Service Knowledge Base
log_info "Creating kb1-customer-service..."
create_kb "kb1-customer-service" "{
    \"name\": \"kb1-customer-service\",
    \"description\": \"Customer service knowledge base for Zava Airlines - rebooking, refunds, complaints, baggage, and passenger assistance\",
    \"retrievalInstructions\": \"Search for airline customer service policies, rebooking procedures, refund guidelines, baggage rules, EU261/DOT compensation, seat upgrade policies, and special assistance requirements.\",
    \"answerInstructions\": \"Provide empathetic, solution-oriented answers about Zava Airlines customer service policies. Always cite the specific policy document. Offer concrete next steps and booking reference guidance. If a situation involves geo-political disruption, recommend checking with the Operations team for the latest route status.\",
    \"outputMode\": \"answerSynthesis\",
    \"knowledgeSources\": [
        {\"name\": \"ks-cs-aisearch\"},
        {\"name\": \"ks-cs-web\"},
        {\"name\": \"ks-cs-sharepoint\"}
    ],
    \"models\": [{
        \"kind\": \"azureOpenAI\",
        \"azureOpenAIParameters\": {
            \"resourceUri\": \"${OPENAI_ENDPOINT}\",
            \"deploymentId\": \"gpt-4.1\",
            \"modelName\": \"gpt-4.1\"
        }
    }],
    \"retrievalReasoningEffort\": {\"kind\": \"medium\"}
}"

# 2. Operations Knowledge Base (includes Bing geo-political source)
log_info "Creating kb2-operations..."
create_kb "kb2-operations" "{
    \"name\": \"kb2-operations\",
    \"description\": \"Operations knowledge base for Zava Airlines - flight ops, disruptions, crew management, and real-time geo-political intelligence via Bing Search\",
    \"retrievalInstructions\": \"Search for flight operations data, disruption management procedures, crew scheduling rules, NOTAM information, airspace closures, and geo-political situations affecting airline routes. Use the Bing Search knowledge source for the latest real-time geo-political intelligence including conflict zones, sanctions, travel bans, and airspace restrictions.\",
    \"answerInstructions\": \"Provide operational insights using IATA codes and aviation terminology. Reference real-time geo-political intelligence from Bing Search when relevant. Include severity assessments for disruptions. Always prioritize safety recommendations. Quantify passenger impact when discussing disruptions.\",
    \"outputMode\": \"answerSynthesis\",
    \"knowledgeSources\": [
        {\"name\": \"ks-ops-aisearch\"},
        {\"name\": \"ks-ops-web\"},
        {\"name\": \"ks-geopolitical-bing\"}
    ],
    \"models\": [{
        \"kind\": \"azureOpenAI\",
        \"azureOpenAIParameters\": {
            \"resourceUri\": \"${OPENAI_ENDPOINT}\",
            \"deploymentId\": \"gpt-4.1\",
            \"modelName\": \"gpt-4.1\"
        }
    }],
    \"retrievalReasoningEffort\": {\"kind\": \"high\"}
}"

# 3. Loyalty Knowledge Base
log_info "Creating kb3-loyalty..."
create_kb "kb3-loyalty" "{
    \"name\": \"kb3-loyalty\",
    \"description\": \"Loyalty program knowledge base for Zava Airlines SkyRewards - miles, tiers, lounge access, partner benefits, and redemption options\",
    \"retrievalInstructions\": \"Search for SkyRewards frequent flyer program details, tier qualification criteria, miles earning and redemption rates, lounge access rules, partner airline benefits, and promotional offers.\",
    \"answerInstructions\": \"Provide enthusiastic, detailed answers about the SkyRewards program. Reference exact mile amounts and tier thresholds. Suggest strategies to maximize miles earning and tier progression. Highlight current promotions when relevant.\",
    \"outputMode\": \"answerSynthesis\",
    \"knowledgeSources\": [
        {\"name\": \"ks-loyalty-aisearch\"},
        {\"name\": \"ks-loyalty-web\"}
    ],
    \"models\": [{
        \"kind\": \"azureOpenAI\",
        \"azureOpenAIParameters\": {
            \"resourceUri\": \"${OPENAI_ENDPOINT}\",
            \"deploymentId\": \"gpt-4.1\",
            \"modelName\": \"gpt-4.1\"
        }
    }],
    \"retrievalReasoningEffort\": {\"kind\": \"medium\"}
}"

log_success "All knowledge bases created successfully!"
echo ""
echo "Knowledge Bases Summary:"
echo "  kb1-customer-service: ks-cs-aisearch + ks-cs-web + ks-cs-sharepoint"
echo "  kb2-operations:       ks-ops-aisearch + ks-ops-web + ks-geopolitical-bing (Bing Search)"
echo "  kb3-loyalty:          ks-loyalty-aisearch + ks-loyalty-web"
