$ErrorActionPreference = "Stop"
$auth = "http://localhost:8001"
$sales = "http://localhost:8002"

$buyer = Invoke-RestMethod -Method Post -Uri "$auth/auth/register" -ContentType "application/json" -Body '{"name":"Maria Silva","email":"maria@example.com","password":"Comprador123!"}'
$buyerToken = (Invoke-RestMethod -Method Post -Uri "$auth/auth/login" -ContentType "application/json" -Body '{"email":"maria@example.com","password":"Comprador123!"}').access_token
$adminToken = (Invoke-RestMethod -Method Post -Uri "$auth/auth/login" -ContentType "application/json" -Body '{"email":"admin@example.com","password":"Admin123!"}').access_token
$adminHeaders = @{Authorization = "Bearer $adminToken"}
$buyerHeaders = @{Authorization = "Bearer $buyerToken"}

$vehicle = Invoke-RestMethod -Method Post -Uri "$sales/vehicles" -Headers $adminHeaders -ContentType "application/json" -Body '{"brand":"Honda","model":"Civic","year":2022,"color":"Preto","price":99000.00}'
Invoke-RestMethod -Method Patch -Uri "$sales/vehicles/$($vehicle.id)" -Headers $adminHeaders -ContentType "application/json" -Body '{"color":"Azul"}' | ConvertTo-Json
Invoke-RestMethod -Method Get -Uri "$sales/vehicles/available" | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$sales/vehicles/$($vehicle.id)/purchase" -Headers $buyerHeaders | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Get -Uri "$sales/vehicles/sold" -Headers $adminHeaders | ConvertTo-Json -Depth 5

