const form = document.querySelector("#productForm");
const imageInput = document.querySelector("#imageInput");
const imagePreview = document.querySelector("#imagePreview");
const uploadText = document.querySelector("#uploadText");
const productGrid = document.querySelector("#productGrid");
const productCount = document.querySelector("#productCount");

let selectedImage = "";
let count = 1;

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.addEventListener("load", () => {
    selectedImage = reader.result;
    imagePreview.src = selectedImage;
    imagePreview.hidden = false;
    uploadText.hidden = true;
  });
  reader.readAsDataURL(file);
});

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const data = Object.fromEntries(new FormData(form));
  const name = data.name.trim();
  const price = data.price.trim();

  if (!selectedImage || !name || !price) {
    return;
  }

  count += 1;
  productCount.textContent = `${count} ¼þÉÌÆ·`;

  const description = [
    data.ip || "IP ´ý²¹³ä",
    data.role || "½ÇÉ«´ý²¹³ä",
    data.category || "Æ·Àà´ý²¹³ä",
  ].join(" ¡¤ ");

  const card = document.createElement("article");
  card.className = "product-card";
  card.innerHTML = `
    <img src="${selectedImage}" alt="${name}">
    <div class="product-info">
      <strong class="product-price">£¤ ${Number(price).toFixed(2)}</strong>
      <h3>${name}</h3>
      <p>${description}</p>
    </div>
  `;
  productGrid.prepend(card);

  form.reset();
  selectedImage = "";
  imagePreview.hidden = true;
  imagePreview.removeAttribute("src");
  uploadText.hidden = false;
});
