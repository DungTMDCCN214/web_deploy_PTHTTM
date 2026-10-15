package vn.ptit.aistudio.dto.diabetes;


public class DiabetesRequest {
    private Integer pregnancies;
    private Double glucose;
    private Double bloodPressure;
    private Double skinThickness;
    private Double insulin;
    private Double bmi;
    private Double diabetesPedigreeFunction;
    private Integer age;

    // Getter và Setter
    public Integer getPregnancies() { return pregnancies; }
    public void setPregnancies(Integer pregnancies) { this.pregnancies = pregnancies; }

    public Double getGlucose() { return glucose; }
    public void setGlucose(Double glucose) { this.glucose = glucose; }

    public Double getBloodPressure() { return bloodPressure; }
    public void setBloodPressure(Double bloodPressure) { this.bloodPressure = bloodPressure; }

    public Double getSkinThickness() { return skinThickness; }
    public void setSkinThickness(Double skinThickness) { this.skinThickness = skinThickness; }

    public Double getInsulin() { return insulin; }
    public void setInsulin(Double insulin) { this.insulin = insulin; }

    public Double getBmi() { return bmi; }
    public void setBmi(Double bmi) { this.bmi = bmi; }

    public Double getDiabetesPedigreeFunction() { return diabetesPedigreeFunction; }
    public void setDiabetesPedigreeFunction(Double diabetesPedigreeFunction) { this.diabetesPedigreeFunction = diabetesPedigreeFunction; }

    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }
}