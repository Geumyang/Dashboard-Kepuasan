## ⚙️ Setup Environment

### Menggunakan Anaconda

```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

### Menggunakan Shell/Terminal

```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

---

## ▶️ Menjalankan Aplikasi Dashboard

Pastikan kamu sudah berada di dalam folder `dashboard/` sebelum menjalankan perintah berikut:

```
streamlit run dashboard.py
```

---