function loadContent(contentId) {
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById(contentId).style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function () {
    loadContent('personal-info'); // 默认显示个人信息
});