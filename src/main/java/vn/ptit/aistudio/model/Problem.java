package vn.ptit.aistudio.model;

/** Một bài toán trong tiểu luận (dùng làm thẻ ở menu và làm trang demo). */
public class Problem {
    private final String id;       // dùng trong URL: /problem/{id} và API: /api/{id}/predict
    private final String chapter;  // tên chương để nhóm ở menu
    private final String icon;
    private final String title;
    private final String model;    // họ mô hình / kỹ thuật
    private final String summary;

    public Problem(String id, String chapter, String icon, String title, String model, String summary) {
        this.id = id; this.chapter = chapter; this.icon = icon;
        this.title = title; this.model = model; this.summary = summary;
    }

    public String getId() { return id; }
    public String getChapter() { return chapter; }
    public String getIcon() { return icon; }
    public String getTitle() { return title; }
    public String getModel() { return model; }
    public String getSummary() { return summary; }
}
