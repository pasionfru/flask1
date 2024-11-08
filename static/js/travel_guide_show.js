document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.reply-button').forEach(button => {
        button.addEventListener('click', () => {
            const form = button.nextElementSibling; // 获取表单
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        });
    });
});
