
const mobileToggle = document.getElementById("mobileToggle");
const navLinks = document.getElementById("navLinks");

mobileToggle?.addEventListener("click", () => {
    const open = navLinks.classList.toggle("open");
    mobileToggle.setAttribute("aria-expanded", open ? "true" : "false");
});

document.querySelectorAll("#navLinks a").forEach(link => {
    link.addEventListener("click", () => navLinks.classList.remove("open"));
});

const revealItems = document.querySelectorAll(".reveal");
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.12 });

revealItems.forEach(item => observer.observe(item));

const sections = document.querySelectorAll("main section[id]");
const navAnchors = document.querySelectorAll('.nav-links a[href^="#"]');

window.addEventListener("scroll", () => {
    let current = "home";
    sections.forEach(section => {
        if (window.scrollY >= section.offsetTop - 150) current = section.id;
    });
    navAnchors.forEach(anchor => {
        anchor.classList.toggle("active", anchor.getAttribute("href") === `#${current}`);
    });
});
