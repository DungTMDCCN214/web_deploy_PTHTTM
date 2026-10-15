<%@ page contentType="text/html;charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<c:set var="pageTitle" value="AI & Deep Learning Studio"/>
<%@ include file="layout/header.jspf" %>

<section class="hero">
  <h1>Khám phá các mô hình học máy và học sâu</h1>
  <p>${total} bài toán thực nghiệm, mỗi bài có một trang demo riêng. Chọn một bài để bắt đầu.</p>
</section>

<c:forEach var="entry" items="${chapters}">
  <h2 class="chapter">${entry.key}</h2>
  <div class="grid">
    <c:forEach var="p" items="${entry.value}">
      <a class="card" href="${ctx}/problem/${p.id}">
        <span class="icon">${p.icon}</span>
        <span class="tag">${p.model}</span>
        <h3>${p.title}</h3>
        <p>${p.summary}</p>
        <span class="open">Mở demo</span>
      </a>
    </c:forEach>
  </div>
</c:forEach>

<c:set var="extraScript" value=""/>
<%@ include file="layout/footer.jspf" %>
