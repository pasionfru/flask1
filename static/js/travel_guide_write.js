document.addEventListener('DOMContentLoaded', () => {
    function autoResize(element) {
        element.style.height = "auto";
        element.style.height = element.scrollHeight + "px";
    }

    // 为 day-item 绑定事件
    function bindDayItemEvents(dayItem, timelineItem) {
        const preInput = dayItem.querySelector('.pre');
        const titleInput = dayItem.querySelector('.title1');
        const contentTextarea = dayItem.querySelector('.content1');
        const timelineTitle = timelineItem.querySelector('.content h4');
        const timelineContent = timelineItem.querySelector('.content p');

        preInput.addEventListener('input', () => {
            timelineTitle.textContent = preInput.value;
        });

        titleInput.addEventListener('input', () => {
            timelineContent.textContent = titleInput.value;
        });

        contentTextarea.addEventListener('input', () => {
            autoResize(contentTextarea);
        });

        // 为 contentTextarea 绑定光标位置更新事件
        bindFocusEvents(contentTextarea);
    }

    function addDayItem(event) {
        event.preventDefault();

        const dayContainer = document.getElementById('day-container');
        const timelineContainer = document.getElementById('timeline');

        const newDayItem = document.createElement('div');
        newDayItem.classList.add('day-item');
        newDayItem.innerHTML = `
            <input class="pre" type="text" value="前言">
            <div class="talk-travel">
                <div class="talk-point">
                    <input class="title1" type="text" value="说说这次旅行">
                    <textarea class="content1">为这次旅行写一段华丽的内容</textarea>
                </div>
                <a class="add_btn" href="#">
                    <img src="../static/css/svg/add.svg" width="30px" height="30px">
                </a>
                <a class="sub_btn" href="#">
                    <img src="../static/css/svg/sub.svg" width="30px" height="30px">
                </a>
            </div>
        `;
        dayContainer.appendChild(newDayItem);

        const newTimelineItem = document.createElement('div');
        newTimelineItem.classList.add('timeline-item');
        newTimelineItem.innerHTML = `
            <div class="circle"></div>
            <div class="content">
                <h4>前言</h4>
                <p>说说这次旅行</p>
            </div>
        `;
        timelineContainer.appendChild(newTimelineItem);

        bindDayItemEvents(newDayItem, newTimelineItem);

        newDayItem.querySelector('.add_btn').addEventListener('click', addDayItem);
        newDayItem.querySelector('.sub_btn').addEventListener('click', (e) => {
            e.preventDefault();
            newDayItem.remove();
            newTimelineItem.remove();
        });
    }

    const initialDayItem = document.querySelector('.day-item');
    const initialTimelineItem = document.querySelector('.timeline-item');
    bindDayItemEvents(initialDayItem, initialTimelineItem);

    document.querySelector('.add_btn').addEventListener('click', addDayItem);
});


// 头图预览和替换
function previewHeadImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.querySelector('.write-bg').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

function previewLocalImages(event) {
    const files = event.target.files;
    const photoGallery = document.getElementById('photoGallery');

    // 遍历所有上传的文件并生成预览
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const reader = new FileReader();

        reader.onload = function (e) {
            const imgElement = document.createElement('li');
            imgElement.innerHTML = `<img src="${e.target.result}" width="86px" height="66px" onclick="insertImage('${e.target.result}')">`;
            photoGallery.appendChild(imgElement);  // 使用 appendChild 追加到现有列表中
        };

        reader.readAsDataURL(file);
    }

    uploadImagesToServer(files);
}

function uploadImagesToServer(files) {
    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
        formData.append('images', files[i]);
    }

    fetch('/upload_user_image', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert('图片上传失败');
            }
        })
        .catch(error => {
            console.error('上传错误:', error);
            alert('图片上传失败');
        });
}

// 插入图片
let focusedTextarea = null;
let cursorPosition = 0;

function bindFocusEvents(textarea) {
    textarea.addEventListener('focus', (event) => {
        focusedTextarea = event.target;
    });

    textarea.addEventListener('keyup', updateCursorPosition);
    textarea.addEventListener('mouseup', updateCursorPosition);
}

function updateCursorPosition(event) {
    cursorPosition = event.target.selectionStart;
}

function insertImage(path) {
    if (focusedTextarea) {
        const imgTag = `![图片](${path})`;

        const value = focusedTextarea.value;
        focusedTextarea.value = value.slice(0, cursorPosition) + imgTag + value.slice(cursorPosition);

        cursorPosition += imgTag.length;
        focusedTextarea.selectionStart = focusedTextarea.selectionEnd = cursorPosition;

        focusedTextarea.focus();
    }
}


// 提交攻略
function submitGuide() {
    const formData = new FormData();

    // 获取标题和头图
    const guideTitle = document.getElementById('guideTitle').value;
    const headImage = document.getElementById('uploadHeadImage').files[0];
    const startDate = document.getElementById('startTime').value;
    const days = document.getElementById('days').value;
    const avgCost = document.getElementById('avgCost').value;

    formData.append('title', guideTitle);  // 确保获取到 title 值
    formData.append('head_img', headImage);
    formData.append('start_time', startDate);  // 确保获取到 start_date 值
    formData.append('days', days);
    formData.append('avgCost', avgCost);  // 确保获取到 avg_cost 值

    // 检查是否成功获取数据
    console.log("Form Data:", guideTitle, startDate, days, avgCost);

    // 获取每个 section 的数据
    const sections = document.querySelectorAll('.day-item');
    sections.forEach((section, index) => {
        formData.append(`sections[${index}][section_pre]`, section.querySelector('.pre').value);
        formData.append(`sections[${index}][section_title]`, section.querySelector('.title1').value);
        formData.append(`sections[${index}][section_content]`, section.querySelector('.content1').value);
    });

    fetch('/submit_guide', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('攻略发表成功！');
            } else {
                alert('攻略发表失败，请重试。');
            }
        })
        .catch(error => console.error('Error:', error));
}
