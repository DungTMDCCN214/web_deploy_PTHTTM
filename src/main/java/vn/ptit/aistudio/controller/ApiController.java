package vn.ptit.aistudio.controller;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * API dùng chung cho mọi bài toán: POST /api/{id}/predict
 * Hiện chỉ trả dữ liệu giả. Khi làm từng bài, tách ra controller riêng
 * (vd. DiabetesController) hoặc thay phần xử lý bên dưới bằng gọi mô hình thật.
 */

import vn.ptit.aistudio.service.DiabetesService;
import vn.ptit.aistudio.common.util.PythonProcessExecutor;
import vn.ptit.aistudio.dto.diabetes.DiabetesRequest;
import vn.ptit.aistudio.dto.diabetes.DiabetesResponse;
@RestController
@RequestMapping("/api")
public class ApiController {

    @PostMapping("/{id}/predict")
    public Map<String, Object> predict(@PathVariable String id, @RequestBody Map<String, Object> input) {
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("problem", id);
        out.put("status", "stub");
        out.put("message", "Chưa gắn mô hình. Đây là dữ liệu giả để kiểm tra luồng giao diện.");
        out.put("received", input);
        return out;
    }
    @Autowired
    private DiabetesService diabetesService;

    @Autowired
    private PythonProcessExecutor pythonExecutor;

    private static final String DIABETES_RAG_SCRIPT = "ml_models/diabetes_rag/analyze.py";
    private static final String STOCK_AGENT_SCRIPT = "ml_models/stock_agent/agent.py";

    @PostMapping("/diabetes/predict")
    public ResponseEntity<DiabetesResponse> predictDiabetes(@RequestBody DiabetesRequest request) {
        DiabetesResponse response = diabetesService.predictRisk(request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        return Map.of("status", "ok");
    }

    @GetMapping("/diabetes-rag/model-info")
    @SuppressWarnings("unchecked")
    public Map<String, Object> diabetesRagModelInfo() {
        return pythonExecutor.execute(DIABETES_RAG_SCRIPT, Map.of("action", "model_info"), Map.class);
    }

    @PostMapping("/diabetes-rag/analyze")
    @SuppressWarnings("unchecked")
    public Map<String, Object> analyzeDiabetesRag(@RequestBody Map<String, Object> input) {
        Map<String, Object> payload = new LinkedHashMap<>(input);
        payload.put("action", "analyze");
        return pythonExecutor.execute(DIABETES_RAG_SCRIPT, payload, Map.class);
    }

    @GetMapping("/stock-agent/model-info")
    @SuppressWarnings("unchecked")
    public Map<String, Object> stockAgentModelInfo() {
        return pythonExecutor.execute(STOCK_AGENT_SCRIPT, Map.of("action", "model_info"), Map.class);
    }

    @GetMapping("/stock-agent/prices")
    @SuppressWarnings("unchecked")
    public Map<String, Object> stockAgentPrices(@RequestParam Map<String, String> query) {
        Map<String, Object> payload = new LinkedHashMap<>(query);
        payload.put("action", "prices");
        return pythonExecutor.execute(STOCK_AGENT_SCRIPT, payload, Map.class);
    }

    @PostMapping("/stock-agent/forecast")
    @SuppressWarnings("unchecked")
    public Map<String, Object> stockAgentForecast(@RequestBody Map<String, Object> input) {
        Map<String, Object> payload = new LinkedHashMap<>(input);
        payload.put("action", "forecast");
        return pythonExecutor.execute(STOCK_AGENT_SCRIPT, payload, Map.class);
    }

    @PostMapping("/stock-agent/ask")
    @SuppressWarnings("unchecked")
    public Map<String, Object> askStockAgent(@RequestBody Map<String, Object> input) {
        Map<String, Object> payload = new LinkedHashMap<>(input);
        payload.put("action", "ask");
        return pythonExecutor.execute(STOCK_AGENT_SCRIPT, payload, Map.class);
    }
}
