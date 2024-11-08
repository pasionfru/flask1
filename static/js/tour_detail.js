//  识别不了 tour.price : js 在客户端执行 ,jinja2模板变量 在服务端渲染
// function calculateTotalPrice() {
//             const pricePerPerson = {{ tour.price }};
//             const adults = document.getElementById('adults').value;
//             const totalPrice = pricePerPerson * adults;
//             document.getElementById('total-price').innerText = 总金额: ¥${totalPrice};
//         }     识别不了 tour.price


//人数 乘 单价
function cal_TotalPrice() {
    // 通过获取 price-info 元素的内容来获取每个人的价格
    const pricePerPerson = parseFloat(document.getElementById('price-info').dataset.price);
    const adults = parseInt(document.getElementById('adults').value);
    // const plane_price = parseFloat(document.getElementById('destination-price').dataset.flightorderamount);
    const totalPrice = pricePerPerson * adults;
    document.getElementById('total-price').innerText = `总金额: ¥${totalPrice} 元`;
}

//搜索航班
function fetchFlights() {
    const departureCity = document.getElementById('departure-city').value;
    const destination = document.getElementById('destination-info').dataset.destination;
    const date = document.getElementById('date').value;

    // 发送请求获取航班信息
    fetch(`/get_flights?departure=${departureCity}&destination=${destination}&date=${date}`)
        .then(response => response.json())
        .then(data => {
            const flightsInfo = document.getElementById('flights-info');
            flightsInfo.innerHTML = ''; // 清空之前的航班信息

            if (data.length === 0) {
                flightsInfo.innerHTML = '<p>没有符合条件的航班。</p>';
            } else {
                let listHTML = '<ul class="flights-list">';
                data.forEach(flight => {
                    listHTML += `
                                <li class="flight-item">
                                    <div class="flight-info">
                                        <p>航班号: ${flight.flight_name}</p>
                                        <p>出发时间: ${flight.departure_time}</p>
                                        <p>到达时间: ${flight.arrival_time}</p>
                                        <p>票价: ¥${flight.order_amount}</p>
                                    </div>
                                </li>
                            `;
                });
                listHTML += '</ul>';
                flightsInfo.innerHTML = listHTML;
            }
        })
        .catch(error => {
            console.error('获取航班信息失败:', error);
        });
}

//提交请求
function submitOrder(tour_id) {
    const date = document.getElementById("date").value;
    const adults = document.getElementById("adults").value;
    const children = document.getElementById("children").value;
    const totalPrice = document.getElementById("total-price").textContent;

    const bookingData = {
        date: date,
        adults: adults,
        children: children,
        totalPrice: totalPrice
    };

    fetch(`/tour_bookings/${tour_id}`, {  // 使用模板变量传递tour.id
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingData)
    })
        .then(response => response.text())
        .then(html => {
            document.open();
            document.write(html);
            document.close();
        })
        .catch(error => console.error('Error:', error));
}

