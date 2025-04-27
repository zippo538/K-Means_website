# Petunjuk Penggunaan Aplikasi Data Mining Pengelompokkan Nilai Try Out

   1. Pastikan memiliki file csv atau bisa [download disini](localhost:8080/download/download-template)    
   ![alt text](/static/content/img/1.png)
   
   2. Selanjutnya, import file tersebut kedalam sistem
   ![alt text](/static/content/img/2.png)

   3. Lihat bar chart disini yaitu menunjukkan nilai 0 setiap fitur di nilai try out. Carilah fitur yang memiliki nilai 0 paling sedikit. Contohnya, diambil pada fitur nilai try out ke-7 sampai dengan 11          
   ![alt text](/static/content/img/3.png)

   4. lalu pilih select kolom yang sudah ditentukan
   ![alt text](/static/content/img/4.png)
   5. Setelah itu klick select Columns
   6. Pindah halaman normalization
   ![alt text](/static/content/img/5.png)

   7. Muncul tabel berisi hasil nilai yang telah di seleksi
   ![alt text](/static/content/img/6.png)

   8. Ingat, pertama pilih **replace with mean** agar tidak terjadi error
   ![alt text](/static/content/img/7.png)

   9. Selanjutnya, pilih **MinMax Scaller** untuk mengubah data nilai menjadi rentang 0-1
   ![alt text](/static/content/img/8.png)

   10. Muncul line *elbow method* yang berguna untuk menentukan nilai cluster terbaik. Cara melihatnya dengan penurunan point diawal yang landai.
   ![alt text](/static/content/img/9.png)

   11. Masukkan nilai k pada kolom ini
   ![alt text](/static/content/img/10.png)

   12. Pindah ke halaman results
   ![alt text](/static/content/img/11.png)

   13. Muncul diagram *scatter plot* yang berisi hasil clustering K-Means
   ![alt text](/static/content/img/12.png)

   14. Disamping kanan, terdapat hasil silhoutte coeficient untuk mengetahui kemiripan data antara satu dengan yang lainnya dalam satu cluster yang sama
   ![alt text](/static/content/img/13.png)

   15. Di halaman bawah, terdapat tabel hasil clustering
   ![alt text](/static/content/img/14.png)

   16. Terdapat 3 tombol yang memiliki fungsi masing-masing yaitu
    ![alt text](/static/content/img/15.png)


* Rekomendasi AI
  ![alt text](/static/content/img/16.png)
  Tombol ini berfungsi memberikan rekomendasi AI untuk menganalisa hasil clustering

* Download Excel
   Tombol ini berguna mendownload hasil clustering berupa file excel
   ![alt text](/static/content/img/17.png)

* Download PDF
   Tombol ini berguna untuk mendownload file hasil clustering berupa PDF
   ![alt text](/static/content/img/18.png)

