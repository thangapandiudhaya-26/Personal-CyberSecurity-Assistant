// ========================================
// CYBERGUARD - MAIN JAVASCRIPT
// ========================================


// ========================================
// SAVE ANALYSIS TO HISTORY
// ========================================

function saveToHistory(type, icon, content, data) {

    let history = JSON.parse(
        localStorage.getItem("cyberguardHistory")
    ) || [];


    const newItem = {

        type: type,

        icon: icon,

        content: content,

        risk_score: data.risk_score,

        risk_level: data.risk_level,

        date: new Date().toLocaleString()

    };


    history.push(newItem);


    localStorage.setItem(
        "cyberguardHistory",
        JSON.stringify(history)
    );

}


// ========================================
// CLEAR RESULT
// ========================================

function clearResult(resultId) {

    const result =
        document.getElementById(resultId);

    if (result) {

        result.style.display = "none";

    }

}


// ========================================
// DISPLAY LIST
// ========================================

function displayList(elementId, items) {

    const list =
        document.getElementById(elementId);

    if (!list) return;


    list.innerHTML = "";


    items.forEach(function (item) {

        const li =
            document.createElement("li");

        li.textContent = item;

        list.appendChild(li);

    });

}


// ========================================
// UPDATE RISK RESULT
// ========================================

function updateRiskResult(

    resultId,
    scoreId,
    badgeId,
    meterId,
    risksId,
    recommendationsId,
    data

) {

    const result =
        document.getElementById(resultId);

    const score =
        document.getElementById(scoreId);

    const badge =
        document.getElementById(badgeId);

    const meter =
        document.getElementById(meterId);


    // Update score

    if (score) {

        score.textContent =
            data.risk_score;

    }


    // Update badge

    if (badge) {

        badge.textContent =
            data.risk_level;

    }


    // Update meter

    if (meter) {

        meter.style.width =
            data.risk_score + "%";

    }


    // Display risks

    displayList(
        risksId,
        data.risks
    );


    // Display recommendations

    displayList(
        recommendationsId,
        data.recommendations
    );


    // Show result

    if (result) {

        result.style.display =
            "block";


        result.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

    }

}


// ========================================
// URL SECURITY CHECKER
// ========================================

async function checkURL() {

    const input =
        document.getElementById(
            "urlInput"
        );


    if (!input) return;


    const url =
        input.value.trim();


    if (!url) {

        alert(
            "Please enter a URL."
        );

        return;

    }


    try {

        const response =
            await fetch(
                "/api/check-url",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        url: url

                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(
                data.message ||
                "Unable to analyze the URL."
            );

            return;

        }


        const checkedURL =
            document.getElementById(
                "checkedURL"
            );


        if (checkedURL) {

            checkedURL.textContent =
                url;

        }


        updateRiskResult(

            "urlResult",

            "urlScore",

            "urlRiskBadge",

            "urlMeter",

            "urlRisks",

            "urlRecommendations",

            data

        );


        // SAVE URL TO HISTORY

        saveToHistory(

            "URL Security Check",

            "🔗",

            url,

            data

        );

    }


    catch (error) {

        console.error(error);

        alert(
            "Unable to connect to the server. Make sure app.py is running."
        );

    }

}


// ========================================
// MESSAGE SCAM CHECKER
// ========================================

async function checkMessage() {

    const input =
        document.getElementById(
            "messageInput"
        );


    if (!input) return;


    const message =
        input.value.trim();


    if (!message) {

        alert(
            "Please enter a message."
        );

        return;

    }


    try {

        const response =
            await fetch(
                "/api/check-message",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        message: message

                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(
                data.message ||
                "Unable to analyze the message."
            );

            return;

        }


        const checkedMessage =
            document.getElementById(
                "checkedMessage"
            );


        if (checkedMessage) {

            checkedMessage.textContent =
                message;

        }


        updateRiskResult(

            "messageResult",

            "messageScore",

            "messageRiskBadge",

            "messageMeter",

            "messageRisks",

            "messageRecommendations",

            data

        );


        // SAVE MESSAGE TO HISTORY

        saveToHistory(

            "Message Scam Check",

            "💬",

            message,

            data

        );

    }


    catch (error) {

        console.error(error);

        alert(
            "Unable to connect to the server. Make sure app.py is running."
        );

    }

}


// ========================================
// EMAIL SECURITY CHECKER
// ========================================

async function checkEmail() {

    const senderInput =
        document.getElementById(
            "emailSender"
        );


    const subjectInput =
        document.getElementById(
            "emailSubject"
        );


    const contentInput =
        document.getElementById(
            "emailContent"
        );


    if (
        !senderInput ||
        !subjectInput ||
        !contentInput
    ) {

        return;

    }


    const sender =
        senderInput.value.trim();


    const subject =
        subjectInput.value.trim();


    const content =
        contentInput.value.trim();


    if (!content) {

        alert(
            "Please enter the email content."
        );

        return;

    }


    try {

        const response =
            await fetch(
                "/api/check-email",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        sender: sender,

                        subject: subject,

                        content: content

                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(
                data.message ||
                "Unable to analyze the email."
            );

            return;

        }


        const checkedEmail =
            document.getElementById(
                "checkedEmail"
            );


        if (checkedEmail) {

            checkedEmail.textContent =
                sender || "No sender entered";

        }


        updateRiskResult(

            "emailResult",

            "emailScore",

            "emailRiskBadge",

            "emailMeter",

            "emailRisks",

            "emailRecommendations",

            data

        );


        // SAVE EMAIL TO HISTORY

        let emailHistoryContent =

            "Sender: " +
            (sender || "Not entered") +

            " | Subject: " +
            (subject || "No subject") +

            " | Content: " +
            content;


        saveToHistory(

            "Email Security Check",

            "📧",

            emailHistoryContent,

            data

        );

    }


    catch (error) {

        console.error(error);

        alert(
            "Unable to connect to the server. Make sure app.py is running."
        );

    }

}


// ========================================
// PAYMENT SCAM CHECKER
// ========================================

async function checkPayment() {

    const input =
        document.getElementById(
            "paymentInput"
        );


    if (!input) return;


    const payment =
        input.value.trim();


    if (!payment) {

        alert(
            "Please enter payment details."
        );

        return;

    }


    try {

        const response =
            await fetch(
                "/api/check-payment",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        payment: payment

                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(
                data.message ||
                "Unable to analyze payment details."
            );

            return;

        }


        const checkedPayment =
            document.getElementById(
                "checkedPayment"
            );


        if (checkedPayment) {

            checkedPayment.textContent =
                payment;

        }


        updateRiskResult(

            "paymentResult",

            "paymentScore",

            "paymentRiskBadge",

            "paymentMeter",

            "paymentRisks",

            "paymentRecommendations",

            data

        );


        // SAVE PAYMENT TO HISTORY

        saveToHistory(

            "Payment Scam Check",

            "💳",

            payment,

            data

        );

    }


    catch (error) {

        console.error(error);

        alert(
            "Unable to connect to the server. Make sure app.py is running."
        );

    }

}