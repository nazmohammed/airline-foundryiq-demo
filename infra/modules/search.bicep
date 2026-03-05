@description('Name of the Azure AI Search service')
param name string

@description('Location for the resource')
param location string

resource searchService 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: name
  location: location
  sku: {
    name: 'basic'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
  }
}

output endpoint string = 'https://${searchService.name}.search.windows.net'
output id string = searchService.id
output name string = searchService.name
