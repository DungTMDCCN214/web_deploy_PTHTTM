<%@ page contentType="text/html;charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<c:set var="pageTitle" value="${problem.title} · AI Studio"/>
<%@ include file="layout/header.jspf" %>

<a class="back" href="${ctx}/">← Về menu</a>
<section class="problem-head">
  <p class="chapter-small">${problem.chapter}</p>
  <h1>${problem.icon} ${problem.title}</h1>
  <p>${problem.summary}</p>
</section>

<%-- Nội dung riêng của từng bài nằm trong problems/{id}.jsp --%>
<jsp:include page="problems/${problem.id}.jsp"/>

<c:set var="extraScript" value="<script src='${ctx}/js/problems/${problem.id}.js'></script>"/>
<%@ include file="layout/footer.jspf" %>
