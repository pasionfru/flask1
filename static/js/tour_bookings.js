function submitBooking(tourId) {
    // 获取联系人信息
    const contactName = document.getElementById("contact_name").value;
    const contactPhone = document.getElementById("contact_phone").value;

    // 获取隐藏字段中的信息，包括出发日期
    const departureDate = document.getElementById("departure_date").value;
    const adults = document.getElementById("adults").value;
    const children = document.getElementById("children").value;
    const totalPrice = document.getElementById("total_price").value;

    // 获取游客信息
    const bookingItems = document.querySelectorAll(".tour-booking-item");
    const travelers = Array.from(bookingItems).map((item, index) => ({
        name: item.querySelector(`input[name="name${index + 1}"]`).value,
        nationality: item.querySelector(`input[name="nationality${index + 1}"]`).value,
        id_number: item.querySelector(`input[name="id${index + 1}"]`).value,
        phone: item.querySelector(`input[name="phone${index + 1}"]`).value
    }));

    // 构造数据对象
    const bookingData = {
        tour_id: tourId,
        departure_date: departureDate,  // 出发日期
        adult_count: adults,
        child_count: children,
        total_price: totalPrice,
        contact_name: contactName,
        contact_phone: contactPhone,
        travelers: travelers
    };

    // 发送 POST 请求到后端
    fetch('/submit_tours_booking', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("订单提交成功！");
        } else {
            alert("订单提交失败，请重试。");
        }
    })
    .catch(error => console.error('Error:', error));
}
