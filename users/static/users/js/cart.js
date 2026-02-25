function deleteFromCart(btn){
    const cartItem = btn.parentElement

    const itemId = cartItem.querySelector('input[name="id"]').value

    fetch(deleteFromCartURL,{
        method: 'POST',
        headers:{
            'X-CSRFTOKEN':CSRFTOKEN
        },
        body:JSON.stringify({
            id:itemId
        })
    })
    .then(res=>res.json())
    .then(data=>updateCartCount(data.cart_item_count))


    cartItem.remove()

}


function checkOut(btn){
    const form = document.getElementById('checkOutForm')

    form.submit()
}