document.getElementById('aiRecommendBtn').addEventListener('click', async function() {
    const btn = this;
    const spinner = document.getElementById('aiSpinner');
    const btnText = document.getElementById('aiButtonText');
    
    // Tampilkan loading
    btn.disabled = true;
    spinner.classList.remove('d-none');
    btnText.textContent = "Memproses...";
    
    try {
        const response = await fetch('/rekomendasi/get_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.redirect) {
            // Langsung redirect jika sudah pernah dipanggil
            window.location.href = data.redirect_url;
        } else if (data.success) {
            // Redirect setelah sukses memproses
            window.location.href = data.redirect_url;
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        alert("Terjadi kesalahan: " + error);
    } finally {
        // Reset tombol
        btn.disabled = false;
        spinner.classList.add('d-none');
        btnText.textContent = "Dapatkan Rekomendasi AI";
    }
});