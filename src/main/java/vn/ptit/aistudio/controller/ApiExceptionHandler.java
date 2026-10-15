
package vn.ptit.aistudio.controller;

import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** Trả lỗi dạng JSON {"message": "..."} để giao diện hiển thị đúng nguyên nhân. */
@RestControllerAdvice(assignableTypes = ApiController.class)
public class ApiExceptionHandler {

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handle(Exception e) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("message", String.valueOf(e.getMessage())));
    }
}
