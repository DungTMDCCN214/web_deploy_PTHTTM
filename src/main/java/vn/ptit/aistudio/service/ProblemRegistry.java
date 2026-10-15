package vn.ptit.aistudio.service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.springframework.stereotype.Component;
import vn.ptit.aistudio.model.Problem;

/**
 * Danh sách bài toán. Thêm / sửa / xóa một bài ở đây là menu tự cập nhật.
 * Nhớ tạo thêm 2 file cùng tên id:
 *   WEB-INF/views/problems/{id}.jsp và static/js/problems/{id}.js
 */
@Component
public class ProblemRegistry {

    private static final String C2 = "Chương 2 · Machine Learning & Deep Neural Network (dữ liệu bảng)";
    private static final String C3 = "Chương 3 · Convolutional Neural Network (thị giác máy tính)";
    private static final String C4 = "Chương 4 · Recurrent Neural Network (chuỗi & thời gian)";
    private static final String C5 = "Chương 5 · Knowledge Graph và Retrieval-Augmented Generation (RAG)";

    private final List<Problem> problems = List.of(
        new Problem("diabetes", C2, "DIA", "Dự báo nguy cơ tiểu đường", "DNN / Transfer Learning", "Dự đoán nguy cơ tiểu đường từ các chỉ số lâm sàng cơ bản."),
        new Problem("housing", C2, "HOME", "Định giá bất động sản", "Random Forest / Ridge", "TODO: mô tả bộ dữ liệu và mục tiêu."),
        new Problem("chatbot", C2, "CHAT", "Chatbot tư vấn sức khỏe", "Knowledge Base", "TODO: mô tả bộ dữ liệu và mục tiêu."),
        new Problem("mnist", C3, "OCR", "Nhận dạng chữ số viết tay (MNIST)", "CNN", "TODO: mô tả bộ dữ liệu và mục tiêu."),
        new Problem("asl", C3, "ASL", "Nhận dạng thủ ngữ (ASL)", "CNN", "TODO: mô tả bộ dữ liệu và mục tiêu."),
        new Problem("stock", C4, "STK", "Dự báo cổ phiếu", "RNN / LSTM / GRU", "TODO: mô tả bộ dữ liệu và mục tiêu."),
        new Problem("gold", C4, "GLD", "Dự báo giá vàng", "LSTM", "TODO: mô tả bộ dữ liệu và mục tiêu."),
        new Problem("ecommerce", C4, "ECOM", "Mô phỏng hành vi e-commerce", "What-if Simulator", "TODO: mô tả bộ dữ liệu và mục tiêu."),
        new Problem("diabetes-rag", C5, "KG", "Trợ lý tiểu đường: Deep Learning + KG + RAG", "Random Forest .sav / KG / TF-IDF RAG", "Demo hợp nhất dự đoán nguy cơ, tri thức y khoa dạng đồ thị và truy xuất bằng chứng văn bản."),
        new Problem("stock-agent", C5, "AG", "Tác tử tài chính: LSTM + KG + RAG (AMZN)", "Forecast Tool / KG / RAG / Agent", "Demo tác tử tài chính điều phối dự báo giá AMZN, đồ thị tri thức, truy xuất bằng chứng và báo cáo tổng hợp.")
    );

    public List<Problem> all() { return problems; }

    public Optional<Problem> find(String id) {
        return problems.stream().filter(p -> p.getId().equals(id)).findFirst();
    }

    public Map<String, List<Problem>> byChapter() {
        return problems.stream().collect(Collectors.groupingBy(
            Problem::getChapter, LinkedHashMap::new, Collectors.toList()));
    }
}
