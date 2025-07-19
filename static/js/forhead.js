"use strict";
let numberElements = document.querySelectorAll(".number");
let numberElementss = document.querySelectorAll(".numberss");
let numberElementsss = document.querySelectorAll(".numbersss");
let numberElementssss = document.querySelectorAll(".numberssss");
let messageElements = document.querySelectorAll(".message");


function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('main');
    const tb = document.querySelector(".toggle-btn")
    sidebar.classList.toggle('hidden');
    main.classList.toggle('full');
    tb.classList.toggle('addentnable')
}

const boxes = document.querySelectorAll(".teacher-card");

boxes.forEach(box => {
    box.addEventListener("mousemove", (e) => {
        const rect = box.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const offsetX = (e.clientX - centerX) / 5;
        const offsetY = (e.clientY - centerY) / 5;

        box.style.transform = `rotateX(${offsetY}deg) rotateY(${-offsetX}deg)`;
    });

    box.addEventListener("mouseleave", () => {
        box.style.transform = "rotateX(0deg) rotateY(0deg)";
    });
});

let currentNumber = 1;
let maxNumber = 100;
let isRunning = true;

function updateNumber() {
    if (currentNumber <= maxNumber && isRunning) {
        numberElements.forEach(el => {
            el.innerText = "+" + currentNumber;
        });
        currentNumber++;
        setTimeout(updateNumber, 10);
    } else if (currentNumber > maxNumber) {
        messageElements.forEach(el => {
            el.innerText = languages[currentLang].finished;
        });
    }
}


updateNumber();

let currentNumbers = 1;
let maxNumbers = 1000;
let isRunnings = true;


function updateNumbers() {
    if (currentNumbers <= maxNumbers && isRunnings) {
        numberElementss.forEach(el => {
            el.innerText = "+" + currentNumbers;
        });
        currentNumbers++;
        setTimeout(updateNumbers, 0, 5);
    } else if (currentNumbers > maxNumbers) {
        messageElements.forEach(el => {
            el.innerText = languages[currentLang].finished;
        });
    }
}

updateNumbers()

let currentNumberss = 1;
let maxNumberss = 90;
let isRunningss = true;


function updateNumberss() {
    if (currentNumberss <= maxNumberss && isRunningss) {
        numberElementsss.forEach(el => {
            el.innerText = "%" + currentNumberss;
        });
        currentNumberss++;
        setTimeout(updateNumberss, 10);
    } else if (currentNumberss > maxNumberss) {
        messageElements.forEach(el => {
            el.innerText = languages[currentLang].finished;
        });
    }
}

updateNumberss()
let currentNumberssss = 1;
let maxNumberssss = 500;
let isRunningssss = true;


function updateNumberssss() {
    if (currentNumberssss <= maxNumberssss && isRunningssss) {
        numberElementssss.forEach(el => {
            el.innerText = "+" + currentNumberssss;
        });
        currentNumbers++;
        setTimeout(updateNumbers, 10);
    } else if (currentNumberssss > maxNumberssss) {
        messageElements.forEach(el => {
            el.innerText = languages[currentLang].finished;
        });
    }
}

updateNumberssss()

