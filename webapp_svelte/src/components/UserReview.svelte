<script lang="ts">
</script>
<div class="shadow-box">
    <form class="form-contact"
        action='https://getform.io/f/agdppwqb' 
        method='POST'
        encType='multipart/form-data'
    >
        
        <div>
            <label for="name">Name</label>
            <input type='text' name='name' required />
        </div>

        <div class="message-box">
            <label for="message">Message</label>
            <textarea rows='5' name='message' required></textarea>
        </div>
        <div class="rating-container">
            <div class="star-rating">
                <input type="radio" name="rating" id="star5" value="5"><label for="star5">&#9733;</label>
                <input type="radio" name="rating" id="star4" value="4"><label for="star4">&#9733;</label>
                <input type="radio" name="rating" id="star3" value="3"><label for="star3">&#9733;</label>
                <input type="radio" name="rating" id="star2" value="2"><label for="star2">&#9733;</label>
                <input type="radio" name="rating" id="star1" value="1" required><label for="star1">&#9733;</label>
            </div>
        </div>
        <div class="button-container">
            <button class='styled-btn'>Send</button>
        </div>
    </form>
</div>

<style>
.shadow-box {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
    max-width: 400px;
    margin: auto;
}

.form-contact {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.form-contact input,
.form-contact textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
}

.message-box {
    display: flex;
    flex-direction: column;
}

/* Rating Section */
.rating-container {
    display: flex;
    flex-direction: column;
    gap: 5px;
    align-items: center;
}
.star-rating {
    display: flex;
    flex-direction: row-reverse;
    justify-content: start;
}

.star-rating input {
    display: none;
}

.star-rating label {
    font-size: 48px;
    color: #ccc;
    cursor: pointer;
    transition: color 0.2s ease-in-out;
}

.star-rating input:checked ~ label {
    color: gold;
}

.star-rating label:hover,
.star-rating label:hover ~ label {
    color: gold;
}

.button-container {
    display: flex;
    justify-content: center;
    margin-top: 10px;
}

.styled-btn {
    background: #007bff;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: 0.3s ease-in-out;
}

.styled-btn:hover {
    background: #0056b3;
}
</style>
