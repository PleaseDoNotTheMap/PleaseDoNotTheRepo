// Adding Alpine.js data model globally
document.addEventListener('alpine:init', () => {
    Alpine.data('model', () => ({
        // form: {
        //     email: '',
        //     username: '',
        //     location: '',
        //     selectedOption: '',
        //     phonenumber: ''
        // },
        allowedURL: [],
        email: '',
        username: '',
        location: '',
        dropdown: '',
        phonenumber: '',
        async submitForm() { 
            try {
                const response = await axios.post('http://localhost:8080/submit', { // Ensure the URL is correct
                    type: "message",
                    // data: this.form,
                      id: 'clientID', // Replace with your actual clientID logic
                    date: Date.now(),
                });

                console.log('Response from server:', response.data);
            } catch (error) {
                console.error('Error sending data:', error);
            }
        }
    }));
});