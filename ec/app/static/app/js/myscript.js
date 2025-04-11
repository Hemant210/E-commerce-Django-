$('.plus-cart').click(function () {
    var prod_id = $(this).attr("pid");
    console.log(prod_id);  // Debug the product ID
    var quantitySpan = this.parentNode.children[2]; 

    $.ajax({
        type: "GET",
        url: "/pluscart",
        data: {
            'prod_id': prod_id
        },
        success: function (data) {
            $(quantitySpan).text(data.quantity);
            $('#amount').text("Rs. " + data.amount);
            $('#totalamount').text("Rs. " + data.totalamount);
        },
        error: function (error) {
            console.error("Error:", error);
        }
    });
});

$('.minus-cart').click(function () {
    var prod_id = $(this).attr("pid");
    var quantitySpan = this.parentNode.children[2];
    var cartRow = $(this).closest('.cart-item');  // You can adjust selector

    $.ajax({
        type: "GET",
        url: "/minuscart",
        data: {
            'prod_id': prod_id
        },
        success: function (data) {
            if (data.quantity === 0) {
                // Remove the item from UI if quantity becomes 0
                cartRow.remove();
            } else {
                $(quantitySpan).text(data.quantity);
            }
            $('#amount').text("Rs. " + data.amount);
            $('#totalamount').text("Rs. " + data.totalamount);
        },
        error: function (error) {
            console.error("Error:", error);
        }
    });
});

$('.remove-cart').click(function () {
    var prod_id = $(this).attr("pid"); // Get the product ID

    var row = $(this).closest('.row');  // Get the parent row

    $.ajax({
        type: "GET",
        url: "/removecart",  // The endpoint for the AJAX request
        data: {
            'prod_id': prod_id  // Sending product ID to the server
        },
        success: function (data) {
            row.remove();  // Remove the item row from the cart
            $('#amount').text("Rs. " + data.amount);  // Update the cart amount
            $('#totalamount').text("Rs. " + data.totalamount);  // Update total amount
          
            if (response.message) {
                showMessage(response.message, 'success');
            }
            $el.fadeOut(500, function () {
                $(this).remove();
            });
        },
        error: function () {
            showMessage('Something went wrong.', 'danger');
        }
    });
});

$('.plus-wishlist').click(function(){
    var id = $(this).attr("pid").toString();  // Fetch the product ID
    console.log("Product ID:", id);  // Debug: Log the product ID

    if (!id) {
        alert("Product ID is missing!");  // Inform the user if ID is empty
        return;
    }

    $.ajax({
        type: "GET",
        url: "/pluswishlist",
        data: { 'prod_id': id },
        success: function (data) {
            console.log("Wishlist Response:", data);  // Debug: Log the response
            window.location.href = `http://localhost:8000/product-detail/${id}`;
        },
        error: function (xhr, status, error) {
            console.error("Error:", error);  // Debug: Log any AJAX errors
            alert("Something went wrong. Please try again.");
        }
    });
});

$('.minus-wishlist').click(function () {
    var id = $(this).attr("pid").toString();  // Fetch the product ID
    console.log("Product ID:", id);  // Debug: Log the product ID

    if (!id) {
        alert("Product ID is missing!");  // Inform the user if ID is empty
        return;
    }

    var button = $(this);  // Reference to the clicked button

    $.ajax({
        type: "GET",
        url: "/minuswishlist",
        data: { 'prod_id': id },
        success: function (data) {
            console.log("Wishlist Response:", data);  // Debug: Log the response
            alert(data.message);  // Notify the user
            button.closest('.wishlist-item').remove();  // Optionally remove the item from the UI
        },
        error: function (xhr, status, error) {
            console.error("Error:", error);  // Debug: Log any AJAX errors
        }
    });
});

