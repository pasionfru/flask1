function updateEndTime() {
    const startTimeInput = document.getElementById("start_time");
    const endTimeSpan = document.getElementById("end_time");

    // 获取选择的时间
    let startTime = startTimeInput.value;
    if (startTime) {
        // 将时间转换为 Date 对象
        const [hours, minutes] = startTime.split(":");
        let startDate = new Date();
        startDate.setHours(parseInt(hours));
        startDate.setMinutes(parseInt(minutes));

        // 增加一小时
        startDate.setHours(startDate.getHours() + 1);

        // 格式化为 HH:MM 格式
        const endHours = String(startDate.getHours()).padStart(2, "0");
        const endMinutes = String(startDate.getMinutes()).padStart(2, "0");

        // 更新显示
        endTimeSpan.textContent = `${endHours}:${endMinutes}`;
    } else {
        // 清空显示
        endTimeSpan.textContent = "-";
    }
}


function submitOrder(guide_id) {
    const serviceDate = document.getElementById("service_date").value;
    const startTime = document.getElementById("start_time").value;
    const endTime = document.getElementById("end_time").textContent;
    const adultCount = document.getElementById("adult_count").value;
    const childCount = document.getElementById("child_count").value;
    const contactName = document.getElementById("contact_name").value;
    const contactPhone = document.getElementById("contact_phone").value;
    const message = document.getElementById("message").value;
    const userId = document.getElementById("user_id").value;

    const bookingData = {
        guide_id: guide_id,  // 动态传入的导游 ID
        service_date: serviceDate,
        start_time: startTime,
        end_time: endTime,
        adult_count: adultCount,
        child_count: childCount,
        contact_name: contactName,
        contact_phone: contactPhone,
        message: message,
        user_id: userId
    };

    fetch('/submit_booking', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("预约成功！");
            } else {
                alert("预约失败，请重试。");
            }
        })
        .catch(error => console.error('Error:', error));
}