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

$body = @{
    cv_text = $sampleCV
} | ConvertTo-Json -Depth 10

Write-Host "Testing CV evaluation endpoint..."
Write-Host "CV Text: $($sampleCV.Substring(0, 100))..."
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/evaluate-cv' -Method Post -Body $body -ContentType 'application/json'
    Write-Host "✅ CV Evaluation Results:"
    Write-Host "========================"
    $evaluation = $response.evaluation
    Write-Host "Technical Score: $($evaluation.technical_score)/40"
    Write-Host "Experience Score: $($evaluation.experience_score)/30"
    Write-Host "Education Score: $($evaluation.education_score)/15"
    Write-Host "Soft Skills Score: $($evaluation.soft_skills_score)/15"
    Write-Host "========================"
    Write-Host "Total Score: $($evaluation.total_score)/100"
    Write-Host ""
    Write-Host "Recommendation: $($evaluation.recommendation)"
    Write-Host ""
    Write-Host "Skills Found: $($evaluation.skills_found -join ', ')"
    Write-Host ""
    Write-Host "Evaluation Summary:"
    Write-Host "$($evaluation.evaluation_summary)"
    Write-Host ""
}
catch {
    Write-Host "❌ Error: $($_.Exception.Message)"
}