document.addEventListener('DOMContentLoaded', function () {
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.getElementById('mainImage');

    initialInfo(thumbnails,mainImage)

    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function () {
            // Remove active class from all thumbnails
            thumbnails.forEach(t => t.classList.remove('active'));

            // Add active class to clicked thumbnail
            this.classList.add('active');

            // Get the image URL from data attribute
            const imageUrl = this.getAttribute('data-image');

            // Update main image
            if (imageUrl) {
                mainImage.src = imageUrl;
            }
        });
    });

    const variantSelectElement = document.getElementById('variantSelect')

    variantSelectElement.addEventListener('change',(event)=>{

        console.log(event.target.selectedOptions[0])
        const selectedVariant = event.target.selectedOptions[0]

        const selectedVariantImageUrl = selectedVariant.getAttribute('data-image')

        const mainImage = document.getElementById('mainImage');

        mainImage.src = selectedVariantImageUrl
    })

    // Variant change handler
    const variantSelect = document.getElementById('variantSelect');
    const productPrice = document.getElementById('productPrice');
    const stockStatus = document.getElementById('stockStatus');
    const stockCount = document.getElementById('stockCount');
    const stockIndicator = document.getElementById('stockIndicator');
    const quantityInput = document.getElementById('quantityInput');

    variantSelect.addEventListener('change', function () {
        const selectedOption = this.options[this.selectedIndex];
        const price = selectedOption.getAttribute('data-price');
        const stock = selectedOption.getAttribute('data-stock');
        const stockStatusValue = selectedOption.getAttribute('data-stock-status');

        // Update price
        productPrice.textContent =price;

        // Update stock count
        stockCount.textContent = stock + ' units available';

        // Update stock status
        stockIndicator.className = 'stock-indicator ' + stockStatusValue;

        if (stockStatusValue === 'in-stock') {
            stockStatus.textContent = 'IN STOCK';
        } else if (stockStatusValue === 'low-stock') {
            stockStatus.textContent = 'LOW STOCK';
        } else if (stockStatusValue === 'out-of-stock') {
            stockStatus.textContent = 'OUT OF STOCK';
        }

        // Update quantity max
        quantityInput.max = stock;
        if (parseInt(quantityInput.value) > parseInt(stock)) {
            quantityInput.value = stock;
        }
    });

    // Quantity controls
    const decreaseBtn = document.getElementById('decreaseQty');
    const increaseBtn = document.getElementById('increaseQty');

    decreaseBtn.addEventListener('click', function () {
        const currentValue = parseInt(quantityInput.value);
        const minValue = parseInt(quantityInput.min);
        if (currentValue > minValue) {
            quantityInput.value = currentValue - 1;
        }
    });

    increaseBtn.addEventListener('click', function () {
        const currentValue = parseInt(quantityInput.value);
        const maxValue = parseInt(quantityInput.max);
        if (currentValue < maxValue) {
            quantityInput.value = currentValue + 1;
        }
    });

    // Tab switching
    const tabs = document.querySelectorAll('.tab');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));

            // Add active class to clicked tab
            this.classList.add('active');

            // Hide all tab panels
            tabPanels.forEach(panel => panel.classList.remove('active'));

            // Show corresponding tab panel
            const tabName = this.getAttribute('data-tab');
            document.getElementById(tabName).classList.add('active');
        });
    });
});


function initialInfo(thumbnails,mainImage){
    const priceElement = document.getElementById('productPrice')
    const firstImage = thumbnails[0].querySelector('img')

    mainImage.src = firstImage.src

    const firstSelectOption = document.getElementById('variantSelect').selectedOptions[0]

    const firstPrice = firstSelectOption.getAttribute('data-price')

    priceElement.textContent = firstPrice


}