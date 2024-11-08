document.addEventListener('DOMContentLoaded', function () {

    const diningDate = document.getElementById('dining_date');
    const diningTime = document.getElementById('dining_time');
    const guestCount = document.getElementById('guest_count');
    const tableCondition = document.getElementById('Table_condition');
    const orderSummary = document.getElementById('order_summary');

    // 更新订单信息
    function updateOrderSummary() {
        const date = diningDate.value || '请选择日期';
        const time = diningTime.value || '请选择时间';
        const guests = guestCount.value || '人数未定';
        const table = tableCondition.options[tableCondition.selectedIndex].text;

        // 更新显示的订单信息
        orderSummary.innerText = `请核对您的订单信息： ${date} / ${time} / ${guests}人 / ${table}`;
    }

    // 监听输入和选择框的变化事件
    diningDate.addEventListener('change', updateOrderSummary);
    diningTime.addEventListener('input', updateOrderSummary);
    guestCount.addEventListener('input', updateOrderSummary);
    tableCondition.addEventListener('change', updateOrderSummary);
});


function submitOrder(catering_id) {
    const diningDate = document.getElementById('dining_date').value;
    const diningTime = document.getElementById('dining_time').value;
    const guestCount = document.getElementById('guest_count').value;
    const tableCondition = document.getElementById('Table_condition').value;
    const contactName = document.getElementById('contact_name').value;
    const contactPhone = document.getElementById('contact_phone').value;
    const remarks = document.getElementById('remarks').value;

    const reservationData = {
        dining_date: diningDate,
        dining_time: diningTime,
        guest_count: guestCount,
        table_condition: tableCondition,
        contact_name: contactName,
        contact_phone: contactPhone,
        remarks: remarks
    };

    fetch(`/submit_reservation/${catering_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(reservationData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("预订成功！");
            } else {
                alert("预订失败，请重试。");
            }
        })
        .catch(error => console.error('Error:', error));
}
