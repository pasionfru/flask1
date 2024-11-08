// 选择地点下拉菜单
function toggleCityDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    if (dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
    } else {
        dropdown.style.display = 'block';
    }
}

//选择城市
//<input class="search-position-box" type="text" id="from" name="from" placeholder="输入国家/地区/城市/机场" readonly>
function selectCity(inputId, cityName) {
    document.getElementById(inputId).value = cityName;
    document.getElementById('city-dropdown-' + inputId).style.display = 'none';
}

// 点击下拉框以外的地方关闭下拉框 监听点击事件
document.addEventListener('click', function (event) {
    // console.log(event.type);
    const dropdowns = document.querySelectorAll('.city-dropdown');//city-dropdown-from city-dropdown-to
    //遍历city-dropdown-to
    dropdowns.forEach(dropdown => {
            if (!dropdown.contains(event.target) && !event.target.matches('.iconfont')) {
                dropdown.style.display = 'none';
            }
        }
    );
});


//单程往返单选框处理
function toggleDateInput() {
    var singleTrip = document.getElementById('singleTrip');
    var roundTrip = document.getElementById('roundTrip');
    var returnDate = document.getElementById('returnDate');

    if (singleTrip.checked) {
        returnDate.disabled = true;
    } else if (roundTrip.checked) {
        returnDate.disabled = false;
    }
}