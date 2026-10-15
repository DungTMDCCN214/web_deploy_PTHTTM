package vn.ptit.aistudio.controller;

import org.springframework.stereotype.Controller;
import org.springframework.http.HttpStatus;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import vn.ptit.aistudio.service.ProblemRegistry;

@Controller
public class PageController {

    private final ProblemRegistry registry;

    public PageController(ProblemRegistry registry) { this.registry = registry; }

    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("chapters", registry.byChapter());
        model.addAttribute("total", registry.all().size());
        return "index";
    }

    @GetMapping("/problem/{id}")
    public String problem(@PathVariable String id, Model model) {
        var p = registry.find(id)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Không có bài toán: " + id));
        model.addAttribute("problem", p);
        return "problem";
    }
}
