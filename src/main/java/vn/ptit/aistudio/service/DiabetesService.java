package vn.ptit.aistudio.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import vn.ptit.aistudio.common.util.PythonProcessExecutor;
import vn.ptit.aistudio.dto.diabetes.DiabetesRequest;
import vn.ptit.aistudio.dto.diabetes.DiabetesResponse;

@Service
public class DiabetesService {

    @Autowired
    private PythonProcessExecutor pythonExecutor;

    private static final String SCRIPT_PATH = "ml_models/diabetes/predict.py";

    public DiabetesResponse predictRisk(DiabetesRequest request) {
        // Nhận trực tiếp đối tượng DiabetesResponse từ Python mà không cần tạo DTO phụ!
        return pythonExecutor.execute(SCRIPT_PATH, request, DiabetesResponse.class);
    }
}