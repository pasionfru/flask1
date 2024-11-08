document.getElementById('hotel-booking-form').addEventListener('submit', function (event) {
    event.preventDefault(); // 阻止表单默认提交行为-提交后刷新

    const destination = document.getElementById('destination').value;
    const keyword = document.getElementById('keyword').value;
    const checkin = document.getElementById('checkin').value;
    const checkout = document.getElementById('checkout').value;

    // 模拟获取酒店信息的请求
    fetch(`/hotel?destination=${destination}&keyword=${keyword}&checkin=${checkin}&checkout=${checkout}`)
        .then(response => response.json())
        .then(data => {
            const hotelList = document.querySelector('.hotel-list');
            hotelList.innerHTML = ''; // 清空之前的酒店信息

            if (data.length === 0) {
                hotelList.innerHTML = '<span>没有符合条件的酒店。</span>';
            } else {
                data.forEach(hotel => {
                    const hotelItem = document.createElement('div');
                    hotelItem.classList.add('hotel-item');
                    hotelItem.onclick = function () {
                        location.href = `/hotel/${hotel.id}`;
                    };

                    hotelItem.innerHTML = `
                                    <img src="${hotel.image_url}" alt="${hotel.title}">
                                    <div class="hotel-item-content">
                                        <h3>${hotel.title}</h3>
                                        <p class="price">${hotel.price} 起</p>
                                        <p class="rating">${hotel.rating} 🌟</p>
                                    </div>
                                `;

                    hotelList.appendChild(hotelItem);
                });
            }
        })
        .catch(error => {
            console.error('获取酒店信息失败:', error);
        });
});