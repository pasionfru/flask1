function openTab(evt, tabId) {
    // 隐藏所有 tab 内容
    var tabContents = document.getElementsByClassName('tab-content');
    for (var i = 0; i < tabContents.length; i++) {
        tabContents[i].style.display = 'none';
        tabContents[i].classList.remove('active');
    }

    // 移除所有 tab -link的激活状态
    var tabLinks = document.getElementsByClassName('tab-link');
    for (var i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove('active');
    }

    // 显示当前点击的 tab 内容
    document.getElementById(tabId).style.display = 'block';
    document.getElementById(tabId).classList.add('active');

    // 为当前 tab 链接添加激活状态
    evt.currentTarget.classList.add('active');
}

