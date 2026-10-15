package vn.ptit.aistudio.dto.diabetes;



public class DiabetesResponse {
    private boolean isDiabetic;
    private double probability;
    private String riskLevel; // Thấp, Trung bình, Cao
    private String advice;    // Lời khuyên sức khỏe

    public DiabetesResponse() {
    }

    public DiabetesResponse(boolean isDiabetic, double probability, String riskLevel, String advice) {
        this.isDiabetic = isDiabetic;
        this.probability = probability;
        this.riskLevel = riskLevel;
        this.advice = advice;
    }

    // Getters
    public boolean isDiabetic() { return isDiabetic; }
    public double getProbability() { return probability; }
    public String getRiskLevel() { return riskLevel; }
    public String getAdvice() { return advice; }

    public void setIsDiabetic(boolean isDiabetic) { this.isDiabetic = isDiabetic; }
    public void setDiabetic(boolean diabetic) { isDiabetic = diabetic; }
    public void setProbability(double probability) { this.probability = probability; }
    public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }
    public void setAdvice(String advice) { this.advice = advice; }
}
