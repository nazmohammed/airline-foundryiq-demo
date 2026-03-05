@description('Name of the Azure AI Services (Foundry) resource')
param name string

@description('Location for the resource')
param location string

@description('OpenAI chat model deployment name')
param modelName string

@description('Embedding model deployment name')
param embeddingModelName string

resource aiServices 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: name
    publicNetworkAccess: 'Enabled'
  }
}

resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aiServices
  name: modelName
  sku: {
    name: 'GlobalStandard'
    capacity: 30
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: '2025-04-14'
    }
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aiServices
  name: embeddingModelName
  sku: {
    name: 'Standard'
    capacity: 30
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: embeddingModelName
      version: '1'
    }
  }
  dependsOn: [chatDeployment]
}

output endpoint string = 'https://${aiServices.properties.customSubDomainName!}.cognitiveservices.azure.com/'
output projectEndpoint string = 'https://${aiServices.properties.customSubDomainName!}.services.ai.azure.com/api/projects/proj1-${name}'
output id string = aiServices.id
output name string = aiServices.name
