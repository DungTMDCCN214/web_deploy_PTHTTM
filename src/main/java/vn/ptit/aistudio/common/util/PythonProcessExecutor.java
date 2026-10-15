package vn.ptit.aistudio.common.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

@Component
public class PythonProcessExecutor {

    private final ObjectMapper mapper = new ObjectMapper();

    /**
     * Linux/Docker (Debian/Ubuntu) chỉ có lệnh "python3", không có "python".
     * Windows thường dùng "python". Có thể ép bằng biến môi trường PYTHON_CMD.
     */
    private static String resolvePythonCommand() {
        String env = System.getenv("PYTHON_CMD");
        if (env != null && !env.isBlank()) {
            return env.trim();
        }
        boolean windows = System.getProperty("os.name", "").toLowerCase().contains("win");
        return windows ? "python" : "python3";
    }

    public <T> T execute(String scriptPath, Object requestInput, Class<T> responseType) {
        try {
            // 1. Chuyển DTO request thành chuỗi JSON
            String jsonInput = mapper.writeValueAsString(requestInput);

            // 2. Kiểm tra file script tồn tại
            File scriptFile = new File(scriptPath);
            if (!scriptFile.exists()) {
                throw new IllegalArgumentException("Không tìm thấy file script Python tại: " + scriptFile.getAbsolutePath());
            }

            // 3. Khởi tạo ProcessBuilder
            ProcessBuilder pb = new ProcessBuilder(resolvePythonCommand(), scriptFile.getAbsolutePath());
            pb.environment().put("PYTHONIOENCODING", "utf-8");
            pb.redirectErrorStream(true); // Gộp stderr vào stdout

            Process process = pb.start();

            try (BufferedWriter writer = new BufferedWriter(
                    new OutputStreamWriter(process.getOutputStream(), StandardCharsets.UTF_8)
            )) {
                writer.write(jsonInput);
            }

            // 4. Đọc toàn bộ luồng stdout từ Python
            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8)
            );

            StringBuilder outputBuilder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                outputBuilder.append(line).append("\n");
            }

            int exitCode = process.waitFor();
            String rawOutput = outputBuilder.toString().trim();

            if (exitCode != 0) {
                System.err.println("=== PYTHON EXECUTION ERROR ===");
                System.err.println(rawOutput);
                throw new RuntimeException("Python script kết thúc với lỗi (code " + exitCode + ")");
            }

            // 5. Trích xuất đoạn JSON {...} hợp lệ duy nhất từ chuỗi rawOutput
            int jsonStart = rawOutput.indexOf("{");
            int jsonEnd = rawOutput.lastIndexOf("}");

            if (jsonStart != -1 && jsonEnd != -1 && jsonEnd > jsonStart) {
                String cleanJson = rawOutput.substring(jsonStart, jsonEnd + 1);
                return mapper.readValue(cleanJson, responseType);
            } else {
                System.err.println("=== RAW PYTHON OUTPUT NON-JSON ===");
                System.err.println(rawOutput);
                throw new IllegalStateException("Không tìm thấy chuỗi JSON hợp lệ trong kết quả trả về từ Python.");
            }

        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("Lỗi khi thực thi Python script [" + scriptPath + "]: " + e.getMessage(), e);
        }
    }
}
