// document.addEventListener('DOMContentLoaded', function() {
//             initializeVariants();
//             setupAddVariantButton();
//         });

//         function initializeVariants() {
//             const formContent = document.querySelector('.form-content');
//             const variantsContainer = document.getElementById('variantsContainer');
            
//             // Get management form first
//             const managementForm = document.querySelector('[name="form-TOTAL_FORMS"]').parentElement;
//             variantsContainer.appendChild(managementForm);
            
//             // Find all variant form paragraphs (they're rendered by Django outside the container)
//             const allParagraphs = Array.from(formContent.querySelectorAll('p'));
            
//             // Group paragraphs by variant index
//             const variantGroups = {};
            
//             allParagraphs.forEach(p => {
//                 // Check if this paragraph contains a variant field
//                 const input = p.querySelector('input, textarea');
//                 if (input && input.name) {
//                     const match = input.name.match(/^form-(\d+)-(.+)$/);
//                     if (match) {
//                         const [, index, fieldName] = match;
//                         if (!variantGroups[index]) {
//                             variantGroups[index] = {
//                                 price: null,
//                                 stock: null,
//                                 attributes: null,
//                                 id: null
//                             };
//                         }
//                         variantGroups[index][fieldName] = p;
//                     }
//                 }
//             });

//             // Create variant cards
//             Object.keys(variantGroups).sort((a, b) => a - b).forEach(index => {
//                 const variant = variantGroups[index];
//                 createVariantCard(index, variant);
//             });
//         }

//         function createVariantCard(index, variant) {
//             const variantsContainer = document.getElementById('variantsContainer');
            
//             // Create variant card
//             const variantCard = document.createElement('div');
//             variantCard.className = 'variant-card';
//             variantCard.dataset.index = index;

//             // Create header
//             const header = document.createElement('div');
//             header.className = 'variant-header';
//             header.innerHTML = `
//                 <div class="variant-title">Variant #${parseInt(index) + 1}</div>
//                 <button type="button" class="delete-variant-btn" onclick="deleteVariant(${index})">Delete</button>
//             `;
//             variantCard.appendChild(header);

//             // Create fields container
//             const fieldsContainer = document.createElement('div');
//             fieldsContainer.className = 'variant-fields';
            
//             // Add price and stock fields
//             if (variant.price) {
//                 fieldsContainer.appendChild(variant.price);
//             }
//             if (variant.stock) {
//                 fieldsContainer.appendChild(variant.stock);
//             }
//             variantCard.appendChild(fieldsContainer);

//             // Create attributes section
//             const attributesSection = document.createElement('div');
//             attributesSection.className = 'attributes-section';
            
//             const attributesHeader = document.createElement('div');
//             attributesHeader.className = 'attributes-header';
//             attributesHeader.innerHTML = `
//                 <div class="attributes-title">Attributes</div>
//                 <button type="button" class="add-attribute-btn" onclick="addAttribute(${index})">+ Add Attribute</button>
//             `;
//             attributesSection.appendChild(attributesHeader);

//             const attributesContainer = document.createElement('div');
//             attributesContainer.id = `attributes-${index}`;
//             attributesSection.appendChild(attributesContainer);

//             variantCard.appendChild(attributesSection);

//             // Add hidden fields (textarea and id)
//             if (variant.attributes) {
//                 const textarea = variant.attributes.querySelector('textarea');
//                 variantCard.appendChild(variant.attributes);
                
//                 // Parse and render attributes
//                 try {
//                     const attrs = JSON.parse(textarea.value);
//                     if (attrs && Array.isArray(attrs)) {
//                         attrs.forEach((attr, attrIdx) => {
//                             addAttributeItem(index, attr, attrIdx);
//                         });
//                     }
//                 } catch (e) {
//                     // Invalid JSON or null
//                 }
//             }

//             if (variant.id) {
//                 variantCard.appendChild(variant.id);
//             }

//             variantsContainer.appendChild(variantCard);
//         }

//         function addAttributeItem(variantIndex, attribute = {name: '', value: ''}, attrIndex = null) {
//             const attributesContainer = document.getElementById(`attributes-${variantIndex}`);
            
//             if (attrIndex === null) {
//                 const currentAttrs = attributesContainer.querySelectorAll('.attribute-item');
//                 attrIndex = currentAttrs.length;
//             }

//             const attributeItem = document.createElement('div');
//             attributeItem.className = 'attribute-item';
//             attributeItem.dataset.attrIndex = attrIndex;
            
//             attributeItem.innerHTML = `
//                 <input type="text" 
//                        placeholder="Name (e.g., Size)" 
//                        value="${attribute.name || ''}"
//                        data-field="name"
//                        onchange="updateAttributesJSON(${variantIndex})">
//                 <input type="text" 
//                        placeholder="Value (e.g., Large)" 
//                        value="${attribute.value || ''}"
//                        data-field="value"
//                        onchange="updateAttributesJSON(${variantIndex})">
//                 <button type="button" 
//                         class="delete-attribute-btn" 
//                         onclick="deleteAttribute(${variantIndex}, ${attrIndex})">×</button>
//             `;

//             attributesContainer.appendChild(attributeItem);
//         }

//         function addAttribute(variantIndex) {
//             addAttributeItem(variantIndex);
//             updateAttributesJSON(variantIndex);
//         }

//         function deleteAttribute(variantIndex, attrIndex) {
//             const attributesContainer = document.getElementById(`attributes-${variantIndex}`);
//             const attributeItem = attributesContainer.querySelector(`[data-attr-index="${attrIndex}"]`);
//             if (attributeItem) {
//                 attributeItem.remove();
//                 updateAttributesJSON(variantIndex);
//             }
//         }

//         function updateAttributesJSON(variantIndex) {
//             const attributesContainer = document.getElementById(`attributes-${variantIndex}`);
//             const attributeItems = attributesContainer.querySelectorAll('.attribute-item');
            
//             const attributes = [];
//             attributeItems.forEach((item, idx) => {
//                 const nameInput = item.querySelector('[data-field="name"]');
//                 const valueInput = item.querySelector('[data-field="value"]');
                
//                 if (nameInput.value || valueInput.value) {
//                     attributes.push({
//                         name: nameInput.value,
//                         value: valueInput.value
//                     });
//                 }
                
//                 // Update data-attr-index
//                 item.dataset.attrIndex = idx;
//                 const deleteBtn = item.querySelector('.delete-attribute-btn');
//                 deleteBtn.onclick = () => deleteAttribute(variantIndex, idx);
//             });

//             const textarea = document.querySelector(`textarea[name="form-${variantIndex}-attributes"]`);
//             if (textarea) {
//                 textarea.value = attributes.length > 0 ? JSON.stringify(attributes) : 'null';
//             }
//         }

//         function deleteVariant(index) {
//             const variantCard = document.querySelector(`.variant-card[data-index="${index}"]`);
//             if (variantCard) {
//                 variantCard.remove();
//             }
//         }

//         function setupAddVariantButton() {
//             const addBtn = document.getElementById('addVariantBtn');
//             const totalFormsInput = document.querySelector('[name="form-TOTAL_FORMS"]');
            
//             addBtn.addEventListener('click', function() {
//                 const currentTotal = parseInt(totalFormsInput.value);
//                 const newIndex = currentTotal;
                
//                 // Create new empty variant structure
//                 const newVariant = {
//                     price: createFormField('price', newIndex, 'number', ''),
//                     stock: createFormField('stock', newIndex, 'number', ''),
//                     attributes: createFormField('attributes', newIndex, 'textarea', 'null'),
//                     id: createFormField('id', newIndex, 'hidden', '')
//                 };

//                 createVariantCard(newIndex, newVariant);
//                 totalFormsInput.value = currentTotal + 1;
//             });
//         }

//         function createFormField(fieldName, index, type, value) {
//             const p = document.createElement('p');
//             const label = document.createElement('label');
//             label.setAttribute('for', `id_form-${index}-${fieldName}`);
//             label.textContent = fieldName.charAt(0).toUpperCase() + fieldName.slice(1) + ':';
            
//             let input;
//             if (type === 'textarea') {
//                 input = document.createElement('textarea');
//                 input.textContent = value;
//             } else {
//                 input = document.createElement('input');
//                 input.type = type;
//                 input.value = value;
//             }
            
//             input.name = `form-${index}-${fieldName}`;
//             input.id = `id_form-${index}-${fieldName}`;
            
//             if (type === 'number') {
//                 input.min = '0';
//             }
            
//             p.appendChild(label);
//             p.appendChild(input);
            
//             return p;
//         }

//         // Update all attributes before form submission
//         document.getElementById('productForm').addEventListener('submit', function(e) {
//             const variantCards = document.querySelectorAll('.variant-card');
//             variantCards.forEach(card => {
//                 const index = card.dataset.index;
//                 updateAttributesJSON(index);
//             });
//         });


function removeAttributeElement(btn){
    btn.parentElement.parentElement.remove()
}

function addAttributeElement(btn){
    const attributeSection = btn.parentElement

    const attributeElement = `
                                    <div class="attribute">
                                        <div class="attribute-item">
                                            <input type="text" value="">
                                            <input type="text" value="">
                                            <button onclick="removeAttributeElement(this)" type="button" class="delete-attribute-btn">
                                                ×
                                            </button>
                                        </div>
                                    </div>
    `
    attributeSection.insertAdjacentHTML('afterend', attributeElement.trim())
}


function addVariant(){
    const varintHTML = `    <div class="variant-card">
                                <div class="variant-header">
                                    <div class="variant-title">Variant</div>
                                    <button onclick="deleteVariant(this)" type="button" class="delete-variant-btn">
                                        Delete
                                    </button>
                                </div>
                                <div class="variant-fields">
                                    <div class="form-group">
                                        <label >Price:</label>
                                        <input type="number" name="variant-2-price" min="0" id="id_variant-2-price">
                                    </div>
                                    <div class="form-group">
                                        <label >Stock:</label>
                                        <input type="number" name="variant-2-stock" min="0" id="id_variant-2-stock">
                                    </div>
                                </div>
                                <div class="attributes-section">
                                    <div class="attributes-header">
                                        <div class="attributes-title">Attributes</div>
                                        <button onclick="addAttributeElement(this)" type="button" class="add-attribute-btn">
                                            + Add Attribute
                                        </button>
                                    </div>
                                    <textarea name="variant-2-attributes" cols="40" rows="10" id="id_variant-2-attributes">null</textarea>
                                    
                                </div>
                            </div>
                            `

        const varinatContainer = document.getElementById('variantsContainer')

        varinatContainer.insertAdjacentHTML('afterbegin',varintHTML)
}



function deleteVariant(btn){
    const variantElement = btn.parentElement.parentElement
    
    const hiddenInput = variantElement.querySelector('.hidden-input input')

    const deletedVariantId = hiddenInput ? hiddenInput.value: null


    if (hiddenInput && deletedVariantId){
        const hiddenContainer = document.getElementById('deletedVariantInputs')

        hiddenContainer.insertAdjacentHTML('afterbegin',`<input hidden type="number" value="${deletedVariantId}">`)
    }

    variantElement.remove()
}

const form = document.getElementById('productForm')

form.addEventListener('submit',e => {

    const variants = document.getElementById('variantsContainer').querySelectorAll('.variant-card')

    const formLength = variants.length

})