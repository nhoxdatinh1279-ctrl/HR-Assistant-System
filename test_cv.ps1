$sampleCV = @"
John Smith - Software Engineer
Education: Master of Science in Computer Science, Stanford University
Experience: 5 years in software development
Skills: Python, Machine Learning, TensorFlow, PyTorch, NLP, LangChain, AWS, Docker
Projects: 
- Built an AI chatbot using LangChain and OpenAI
- Developed ML models for text classification
- Deployed cloud applications on AWS
- Led a team of 4 developers on an AI project
Certifications: AWS Certified Solutions Architect
Soft Skills: Team leadership, excellent communication, problem-solving, innovation
"@

$message = "Please evaluate this CV: " + $sampleCV

$body = @{
    message = $message
} | ConvertTo-Json -Depth 10

Write-Host "Sending CV evaluation request..."
$response = Invoke-RestMethod -Uri 'http://localhost:8000/api/chat' -Method Post -Body $body -ContentType 'application/json'
$response | ConvertTo-Json -Depth 10