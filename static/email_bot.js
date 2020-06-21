const emailForm = document.getElementById('email-feedback-form');

emailForm.addEventListener('submit', e => {
    e.preventDefault();
    console.log(`Email entered : ${document.querySelector('#feedback-input-email').value}`);
    console.log(`Name entered : ${document.querySelector('#feedback-input-name').value}`);
    console.log(`Message entered : ${document.querySelector('#feedback-input-message').value}`);

    var current = new Date();

    Email.send({
        SecureToken : "70a6f39e-277e-43b4-a89d-60c210503976",
        To : 'gpshreevathsa@gmail.com, akhilskasturi@outlook.com',
        From : "myp1080.email@gmail.com",
        Subject : `Message from --> ${document.querySelector('#feedback-input-name').value} @ ${document.querySelector('#feedback-input-email').value}`,
        Body : `<strong>Name:</strong> ${document.querySelector('#feedback-input-name').value}<br><strong>Email:</strong> ${document.querySelector('#feedback-input-email').value}<br><strong>Time:</strong> ${current.getDate()}/${current.getMonth() + 1}/${current.getFullYear()} @ ${current.getHours()}:${current.getMinutes()}<br><br><strong>The message you recieved was as follows:</strong><br>--------------------<br> <em>${document.querySelector('#feedback-input-message').value}</em><br>--------------------<br><br><br><strong><em>Regards,<br>The MYP-1080 Email Team</strong></em>`
    })
    
    emailForm.outerHTML = `
    <div class="container 75%">
        <div class="row uniform 50%">
            <div style='width: 100%'>
                <p style='text-align: center'>--------</p>
            </div>
            <div style='width: 100%'>
                <h4 style='text-align: center; text-transform: none;'>The Feedback has been sent!</h4>
            </div>
            <div style='width: 100%; margin-bottom: 15px;'>
                <p style='text-align: center'>--------</p>
            </div>
        </div>
    </div>
    `

})