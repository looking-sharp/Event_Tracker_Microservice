const reviews_div = document.getElementById('reviews');
const loading_div = document.getElementById('loading');
const pages_div = document.getElementById('pages')

const left_arrow = document.getElementById('arrow-left');
const page_num = document.getElementById('page-num');
const right_arrow = document.getElementById('arrow-right');
var low = 0;
var high = 10;
var curPage = 1;

function get_reviews(start, end) {
    loading_div.style.display = "grid";
    reviews_div.style.display = "none";
    fetch(`/get-reviews?start=${start}&end=${end}`)
        .then(data => data.json())
        .then(reviews => {
            if (reviews.length === 0) {
                const review_el = document.createElement("div");
                review_el.classList.add("review-fail");
                review_el.innerHTML += `<p>No Reviews Found</p>`;
                pages_div.parentNode.insertBefore(review_el, pages_div);
            }
            reviews.forEach(review => {
                const rating = review.rating ?? 0;

                const review_el = document.createElement("div");
                review_el.classList.add("review");

                review_el.innerHTML = `
                    <p><span>${review.userId} -- </span><span class="stars active">${"★".repeat(rating)}</span><span class="stars non-active">${"★".repeat(5 - rating)}</span></p>
                    <p class="comment">${review.comment}</p>
                `;

                pages_div.parentNode.insertBefore(review_el, pages_div);
            });
            setTimeout(() => {
                reviews_div.style.display = "grid";
                loading_div.style.display = "none";
            }, 500);
        })
        .catch(err => {
            loading_div.textContent = "Failed to load reviews.";
            console.error(err);
        });
}

function clear_reviews() {
    const divsToRemove = document.querySelectorAll('div.review');
    const fail_div = document.querySelector('div.review-fail');
    divsToRemove.forEach(div => {
        div.remove();
    });
    if (fail_div != null) {
        fail_div.remove()
    }
}

document.addEventListener("DOMContentLoaded", () => {
    get_reviews(0,10);
});

left_arrow.addEventListener('click', () => {
    if(curPage === 1) {
        return;
    }
    curPage--;
    page_num.textContent = `${curPage}`;
    high = 10 * curPage;
    low = high - 10;
    clear_reviews()
    get_reviews(low,high);
});

right_arrow.addEventListener('click', () => {
    const fail_div = document.querySelector('div.review-fail');
    if(fail_div != null) {
        return;
    }
    curPage++;
    page_num.textContent = `${curPage}`;
    high = 10 * curPage;
    low = high - 10;
    clear_reviews()
    get_reviews(low,high);
});