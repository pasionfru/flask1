function loadContent(contentId) {
    const contentSections = document.querySelectorAll('.content-section');
    contentSections.forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById(contentId).style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function () {
    loadContent('flight-management'); // 默认显示航班管理
});