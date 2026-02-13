

let variantCardLength = 0

let deletedImageIds = []

let deletedVariantIds = []

function isValid(value) {
  return value !== null && 
         value !== undefined && 
         value !== '' && 
         !(typeof value === 'string' && value.trim() === '');
}

function removeAttributeElement(btn) {
    btn.parentElement.parentElement.remove()
}

function addAttributeElement(btn) {
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

const dataTransferObject = {}

function addImage(e) {
    const imageConatiner = e.parentElement.querySelector('.images-grid')
    const hiddenImageField = e.parentElement.querySelector('input')


    const newFileInput = document.createElement('input');
    newFileInput.type = 'file';
    newFileInput.multiple = true; // Allow multiple selection

    newFileInput.addEventListener('change',()=>{
        const file = newFileInput.files[0]

        if (!file) return;

        // append file to DataTransfer

        const key = hiddenImageField.name

        dataTransferObject[key] = dataTransferObject[key] ?? new DataTransfer()

        dataTransferObject[key].items.add(file);

        // assign back to input


        newFileInput.files = dataTransferObject[key].files;

        newFileInput.value = "";

        hiddenImageField.files = dataTransferObject[key].files

        showPreview(file,imageConatiner)

    })

    newFileInput.click()
}

function getFileId(file){
    return `${file.name}-${file.size}-${file.lastModified}`;
}

function showPreview(file,imagesContainer) {
 const imgUrl = URL.createObjectURL(file);
 const fileId = getFileId(file)

    const html = `
        <div class="image-item">
            <img data-existingImage="false" id="${fileId}" class="image-preview" src="${imgUrl}" onload="URL.revokeObjectURL(this.src)">
            <div class="image-info">
                <div class="image-actions">
                    <button onclick="deleteImage(this)" type="button" class="delete-image-btn-card">
                        Delete
                    </button>
                </div>
            </div>
        </div>
    `;
    
    imagesContainer.insertAdjacentHTML('beforeend', html);

}

function deleteImage(btn){
    const imageContainer = btn.parentElement.parentElement.parentElement
    const img = imageContainer.querySelector('img')

    const imgId = img.id

    const existingImage = img.dataset.existingimage

    if (existingImage === 'false'){

        if (isValid(imgId) === true){
            const imageSection = imageContainer.parentElement.parentElement

            const input = imageSection.querySelector('input')

            const dataTransferKey = input.name

            const dataTransfer = dataTransferObject[dataTransferKey]

            const newDataTransfer = new DataTransfer()

            if (dataTransfer){
                const imageFiles = dataTransfer.files


                for (let index = 0; index < imageFiles.length; index++) {
                    
                    const imageFile = imageFiles[index];

                    const imageFileId = getFileId(imageFile)

                    if (imgId !== imageFileId) newDataTransfer.items.add(imageFile)
                    
                    
                    
                }
            }

            dataTransferObject[dataTransferKey] = newDataTransfer

            input.files = newDataTransfer.files
        }
    }

    else{
        const imageId = imgId.split('-')
        deletedImageIds.push(imageId.at(-1))

    }


    imageContainer.remove()
    // console.log(imageContainer)

}




function addVariant() {
    const newIndex = variantCardLength
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
                                        <input type="number" name="variant-${newIndex}-price" min="0">
                                    </div>
                                    <div class="form-group">
                                        <label >Stock:</label>
                                        <input type="number" name="variant-${newIndex}-stock" min="0">
                                    </div>
                                </div>
                                 <div class="images-section">
                                    <div class="images-header">
                                        <div class="subsection-title">Images</div>
                                    </div>
                                    <input data-index="" type="file" name="variant-${newIndex}-image_input_field" multiple=""
                                        id="id_variant-${newIndex}-image_input_field">
                                    <div class="image-upload-area" onclick="addImage(this)">
                                        <div class="upload-icon">📷</div>
                                        <div class="upload-text">Click to upload</div>
                                        <div class="upload-hint">PNG, JPG, GIF up to 10MB</div>
                                    </div>
                                    <div class="images-grid">
                                    </div>
                                </div>
                                <div class="attributes-section">
                                    <div class="attributes-header">
                                        <div class="attributes-title">Attributes</div>
                                        <button onclick="addAttributeElement(this)" type="button" class="add-attribute-btn">
                                            + Add Attribute
                                        </button>
                                    </div>
                                    <textarea name="variant-${newIndex}-attributes" cols="40" rows="10">null</textarea>
                                    
                                </div>
                            </div>
                            `

    const varinatContainer = document.getElementById('variantsContainer')

    varinatContainer.insertAdjacentHTML('afterbegin', varintHTML)

    variantCardLength+=1
}


function dataTranserCleanUp(variantElement){
    const input = variantElement.querySelector('.images-section input')

    const imageKey = input.name

    delete dataTransferObject[imageKey]
}


function deleteVariant(btn) {
    const variantElement = btn.parentElement.parentElement

    dataTranserCleanUp(variantElement)

    // Move the delete variant id to deleteInputs

    const varianInput = variantElement.querySelector('.variant-fields .hidden-input input')

    if (isValid(varianInput)) deletedVariantIds.push(varianInput.value)
    

    variantElement.remove()
}


function attributesTypeConversion(attributeInputs, textArea) {

    const attributesArray = []
    for (let index = 0; index < attributeInputs.length; index += 2) {

        const name = attributeInputs[index]?.value?.trim()
        const value = attributeInputs[index + 1]?.value?.trim()

        if (name &&
            value &&
            name !== "undefined" &&
            value !== "undefined" &&
            name !== "null" &&
            value !== "null"
        ) {
            attributesArray.push({ name: name, value: value })
        }

    }

    textArea.value = JSON.stringify(attributesArray)

}

function getIndexes(length, initalDataIndexes) {
    const result = [];
    let num = 0; // starting number

    while (result.length < length) {
        if (!initalDataIndexes.has(String(num))) {
            result.push(num);
        }
        num++;
    }

    return result;
}


function fixFieldsIndex(variantCards) {

    for (let index = 0; index < variantCards.length; index++) {
        const card = variantCards[index];

        const fields = card.querySelectorAll('.variant-fields input,.attributes-section textarea,.images-section input')

        for (let i = 0; i < fields.length; i++) {
            const field = fields[i];

            const nameVals = field.name.split('-')

            const [prefix, fieldName, fieldIndex] = [nameVals[0], nameVals.at(-1), index]

            field.name = `${prefix}-${fieldIndex}-${fieldName}`


        }



    }
}

function fixHiddenFormFields(formLength) {
    const hiddenInputContainer = document.getElementById('hiddenInputs')

    const initialFormInput = hiddenInputContainer.querySelector('input[name="variant-INITIAL_FORMS"]')

    const totalFormInput = hiddenInputContainer.querySelector('input[name="variant-TOTAL_FORMS"]')

    initialFormInput.value = 0
    totalFormInput.value = formLength
}

function getInitialDataIndexes(variantCards) {

    const indexes = new Set()

    variantCards.forEach(card => {
        const hiddenIdContainer = card.querySelector('.variant-fields .hidden-input')

        if (hiddenIdContainer) {
            const index = hiddenIdContainer.querySelector('input').name.split('-')[1]
            indexes.add(String(index))
        }
    });

    return indexes
}

function handleDeletedInputs(){

    const deletedInputsContainer = document.getElementById('deleteInputs')
    const deletedImageInput = deletedInputsContainer.querySelector('#imageInputContainer textarea')

    const deletedVariantInput =  deletedInputsContainer.querySelector('#variantIdContainer textarea')

    deletedImageInput.value = JSON.stringify(deletedImageIds)

    deletedVariantInput.value = JSON.stringify(deletedVariantIds)
        
}

const form = document.getElementById('productForm')

form.addEventListener('submit', e => {

    const variantCards = document.getElementById('variantsContainer').querySelectorAll('.variant-card')

    const formLength = variantCards.length

    variantCards.forEach(card => {
        attributeSection = card.querySelector('.attributes-section')

        attributeInputs = attributeSection.querySelectorAll('.attribute input')

        textArea = attributeSection.querySelector('textarea')

        attributesTypeConversion(attributeInputs, textArea)

    });

    // indexes = getInitialDataIndexes(variantCards)

    fixFieldsIndex(variantCards)
    fixHiddenFormFields(formLength)

    handleDeletedInputs()

})

document.addEventListener('DOMContentLoaded',()=>{

    variantCardLength = document.getElementById('variantsContainer').querySelectorAll('.variant-card').length

})
