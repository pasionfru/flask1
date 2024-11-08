function updateGuestInfo() {
    const guestInfoContainer = document.getElementById('guest-info');
    const roomCount = document.getElementById('room-count').value;
    guestInfoContainer.innerHTML = '<h3>住客资料</h3>';
    for (let i = 1; i <= roomCount; i++) {
        guestInfoContainer.innerHTML += `
                    <div class="guest-section" id="guest-section-${i}">
                        <h4>房间 ${i}</h4>
                        <label for="guest-name-${i}">住客姓名</label>
                        <input type="text" id="guest-name-${i}" name="guest-name-${i}" placeholder="每间只需填写一人" required>
                        <label for="guest-email-${i}">电子邮件 (选填)</label>
                        <input type="email" id="guest-email-${i}" name="guest-email-${i}" placeholder="电子邮件">
                        <label for="guest-phone-${i}">电话号码</label>
                        <input type="tel" id="guest-phone-${i}" name="guest-phone-${i}" placeholder="电话号码" required>
                    </div>
                `;
    }
}