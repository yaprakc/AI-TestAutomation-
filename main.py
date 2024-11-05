import sys
import tempfile
import tkinter as tk
from tkinter import ttk
import google.generativeai as genai
import unittest
from io import StringIO
import timeit
import threading
import time
import subprocess
import os
import re
from unittest.mock import patch

GOOGLE_API_KEY = "Your_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Dil seçenekleri
PYTHON = "Python"
JAVA = "Java"

# Standart prompt
STANDARD_PROMPT = """
Lütfen aşağıda verilen kodun öncelikle dilini algıla ve kod için hata alabilecek kısımlar için farklı değerler kullanarak birim testleri, entegrasyon testi ve performans testi oluşturun. Python'un kendi kütüphaneleri dışında hiçbir import kullanma. Açıklama ya da yorum satırı olmasın, sadece kodları yaz.
Performans testi için oluşturulan kodda class adı TestPerformans, fonksiyon adı ise test_performans olarak oluşturulacak.

Testlerde girdi alımı için input fonksiyonunu unittest.mock.patch kullanarak taklit et.
Main kullanma.

Function_Code:
{function_code}
"""

JAVA_PROMPT = """
Lütfen aşağıda verilen kodun önce dilini algıla eğer javaysa Java kodunu test etmek için birim testleri oluşturun ama kesinlikle türkçe karakter kullanma.
JUnit 4 kullanarak test kodlarını yazın ama kesinlikle türkçe karakter kullanma.
Java'nın kendi kütüphaneleri dışında hiçbir import kullanmayın.
Açıklama veya yorum satırı olmasın, sadece kodları yazın.


Function_Code:
{function_code}
"""
def detect_language(code):
    #python ve javaya özgü bazı karakteristik özellikleri kontrol ediyoruz
    if re.search(r'\b(def|from)\b', code):
        return 'python'
    elif re.search(r'\b(public|class|static|void)\b', code):
        return 'java'
    else:
        #Belirli bir dil tespit edilemezse, varsayılan olarak Python kabul ediyoruz
        return 'python'

def generate_test_cases(function_code, language):
    if language == 'python':
        prompt = STANDARD_PROMPT.format(function_code=function_code)
    elif language == 'java':
        prompt = JAVA_PROMPT.format(function_code=function_code)
    else:
        return "Bilinmeyen dil"

    response = model.generate_content(prompt)
    #Metin ayıklama
    generated_text = response.candidates[0].content.parts[0].text.strip()
    print("Generated Text:\n", generated_text)
    return generated_text


#geminiden sadece kodları alma
def extract_code_blocks(generated_text, language='python'):
    code_blocks = []
    if language == 'java':
        #Java kodu için tüm metni bir blok olarak alıyoruz
        code_blocks = [generated_text]
    else:
        in_code_block = False
        code_block = []
        for line in generated_text.splitlines():
            if line.strip().startswith("```python"):
                in_code_block = True
            elif line.strip().startswith("```") and in_code_block:
                in_code_block = False
                code_blocks.append("\n".join(code_block))
                code_block = []
            elif in_code_block:
                code_block.append(line)
    return code_blocks


def extract_java_code_blocks(generated_text):
    #kod bloklarını ayıklama
    java_code_blocks = []
    in_code_block = False
    code_block = []

    for line in generated_text.splitlines():
        if line.strip().startswith("```java"):
            in_code_block = True
        elif line.strip().startswith("```") and in_code_block:
            in_code_block = False
            if code_block:
                java_code_blocks.append("\n".join(code_block))
                code_block = []
        elif in_code_block:
            code_block.append(line)

    #eğer son kod bloğu kodu tamamlanmamışsa, ekliyoruz
    if code_block:
        java_code_blocks.append("\n".join(code_block))

    return java_code_blocks

def clean_java_code(java_code):
    #İstenmeyen karakterleri temizliyoruz
    java_code_cleaned = ""
    in_code_block = False

    for line in java_code.splitlines():
        if line.strip().startswith("```java") or line.strip().startswith("```"):
            continue  #kod blokları için işaretleri atlıyoruz
        java_code_cleaned += line + "\n"

    return java_code_cleaned.strip()

def run_tests(code_blocks):
    test_output = StringIO()

    try:
        for code in code_blocks:
            exec(code, globals())
        test_loader = unittest.TestLoader()
        test_suite = test_loader.loadTestsFromModule(sys.modules[__name__])
        test_runner = unittest.TextTestRunner(stream=test_output, verbosity=2)
        test_runner.run(test_suite)
    except SyntaxError as e:
        return f"Sözdizimi hatası: {e.text} (satır {e.lineno}, karakter {e.offset})"
    except Exception as e:
        return f"Testler çalıştırılırken bir hata oluştu: {e}"

    return test_output.getvalue()

def run_performance_tests(code_blocks):
    timeit_output = StringIO()

    try:
        #testlerin yüklenmesi ve çalıştırılması
        for code in code_blocks:
            exec(code, globals())
        #performans testini çağırmma ve test etma
        setup_code = "\n".join(code_blocks)
        test_code = "TestPerformans().test_performans()"
        elapsed_time = timeit.timeit(test_code, setup=setup_code, number=1)
        #sonuçlar
        timeit_output.write(f"TestPerformans().test_performans() süresi: {elapsed_time:.6f} saniye\n")
    except SyntaxError as e:
        return f"Sözdizimi hatası: {e.text} (satır {e.lineno}, karakter {e.offset})"
    except Exception as e:
        return f"Performans testleri çalıştırılırken bir hata oluştu: {e}"

    return timeit_output.getvalue()

def extract_class_name(java_code):
    #public class ifadesini arama
    match = re.search(r'public\s+class\s+(\w+)', java_code)

    if not match:
        #class anahtar kelimesinin bulunduğu diğer durumları da kontrol ediyoruz
        match = re.search(r'class\s+(\w+)', java_code)
    if match:
        return match.group(1)
    else:
        return None

def run_java_tests(java_test_code, original_java_code):
    # java kodunu temizleme
    original_java_code_cleaned = clean_java_code(original_java_code)
    java_test_code_cleaned = clean_java_code(java_test_code)
    #Orijinal Java kodunu dosyaya yazma
    original_class_name = extract_class_name(original_java_code_cleaned)
    if not original_class_name:
        return "Orijinal Java kodunda sınıf adı bulunamadı."

    temp_dir = tempfile.gettempdir()
    original_java_file = os.path.join(temp_dir, f"{original_class_name}.java")
    with open(original_java_file, 'w') as temp_file:
        temp_file.write(original_java_code_cleaned)

    #test java kodunu dosyaya yazma
    test_class_name = extract_class_name(java_test_code_cleaned)
    if not test_class_name:
        return "Test Java kodunda sınıf adı bulunamadı."

    java_test_file = os.path.join(temp_dir, f"{test_class_name}.java")
    with open(java_test_file, 'w') as temp_file:
        temp_file.write(java_test_code_cleaned)

    #JAR dosyalarının tam yolu
    junit_jar_path = "junit-4.12.jar dosya yolu"
    hamcrest_jar_path = "hamcrest-core-1.3.jar dosya yolu"

    #orijinal java kodunu derlema
    result = subprocess.run(["javac", original_java_file], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Sözdizimi hatası (Orijinal kod): {result.stderr}")
        return f"Sözdizimi hatası (Orijinal kod): {result.stderr}"
    #test java kodunu derleme
    result = subprocess.run(["javac", "-cp", f".;{temp_dir};{junit_jar_path};{hamcrest_jar_path}", java_test_file], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Sözdizimi hatası (Test kodu): {result.stderr}")
        return f"Sözdizimi hatası (Test kodu): {result.stderr}"

    #testleri çalıştırıyoruz
    result = subprocess.run(
        ["java", "-cp", f".;{temp_dir};{junit_jar_path};{hamcrest_jar_path}", "org.junit.runner.JUnitCore", test_class_name],
        capture_output=True, text=True, cwd=temp_dir
    )
    if result.returncode != 0:
        print(f"Test hatası: {result.stderr}\nÇalıştırma hatası: {result.stdout}")
        return f"Test hatası: {result.stderr}\nÇalıştırma hatası: {result.stdout}"

    print(result.stdout)  #test sonuçlarını doğrudan terminale yazdırma

    return result.stdout

def display_results(function_code, result_text_widget):
    language = detect_language(function_code)
    generated_code = generate_test_cases(function_code, language)
    code_blocks = extract_code_blocks(generated_code, language)

    result_text_widget.delete(1.0, tk.END)
    result_text_widget.insert(tk.END, "Oluşturulan test senaryoları:\n")
    result_text_widget.insert(tk.END, generated_code + "\n\n")

    if language == 'java':
        java_test_output = run_java_tests(code_blocks[0], function_code)
        result_text_widget.insert(tk.END, "Java test sonuçları:\n", "java_output")
        result_text_widget.insert(tk.END, java_test_output + "\n")
    else:
        if function_code.strip():
            function_code_lines = function_code.split('\n')
            function_code_str = "\n".join([line for line in function_code_lines if line.strip()]) + "\n"
            code_blocks = [function_code_str + code for code in code_blocks]

        if any("unittest" in code for code in code_blocks):
            test_results = run_tests(code_blocks)
            result_text_widget.insert(tk.END, "Birim ve entegrasyon test sonuçları:\n")

            for line in test_results.splitlines():
                if "FAIL" in line or "ERROR" in line:
                    result_text_widget.insert(tk.END, line + "\n", "error")
                elif "ok" in line:
                    result_text_widget.insert(tk.END, line + "\n", "success")
                else:
                    result_text_widget.insert(tk.END, line + "\n")

            result_text_widget.insert(tk.END, "\n")

        if any("test_performans" in code for code in code_blocks):
            performance_results = run_performance_tests(code_blocks)
            result_text_widget.insert(tk.END, "Performans test sonuçları:\n")

            if "Performans testleri çalıştırılırken bir hata oluştu" in performance_results:
                result_text_widget.insert(tk.END, performance_results + "\n", "error")
            else:
                result_text_widget.insert(tk.END, performance_results + "\n", "success")
        else:
            result_text_widget.insert(tk.END, "Performans testleri bulunamadı.\n")

#hızlandırmak için thread
def threaded_display_results(function_code, result_text_widget):
    thread = threading.Thread(target=display_results, args=(function_code, result_text_widget))
    thread.start()
    progress_bar.start()
    progress_bar['maximum'] = 100

    for i in range(100):
        time.sleep(0.08)
        progress_bar['value'] = i
        progress_label.config(text=f"İşlem devam ediyor: {i}%")
        root.update_idletasks()

    progress_bar.stop()
    progress_label.config(text="İşlem tamamlandı.")

#pencere oluşturma
root = tk.Tk()
root.title("Dinamik Fonksiyon Testi")
root.geometry("800x800")

#etiket ve progress bar ekleme
progress_label = tk.Label(root, text="GenAI ile iletişim kuruluyor...")
progress_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='determinate')
progress_bar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

#fonksiyon girme alanı ekleme
tk.Label(root, text="Fonksiyonu Girin:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
function_code_text = tk.Text(root, height=15, width=200)
function_code_text.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

#test sonuçları için kaydırılabilir metin alanı ekleme
result_text_widget = tk.Text(root, height=25, width=100, wrap='word')
result_text_widget.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

#kaydırma çubuğu ekleme
scrollbar = tk.Scrollbar(root, command=result_text_widget.yview)
scrollbar.grid(row=4, column=1, sticky='nsew')
result_text_widget.config(yscrollcommand=scrollbar.set)

#farklı sonuç türleri için etiket renklerini tanımlama
result_text_widget.tag_configure("error", foreground="red")
result_text_widget.tag_configure("failure", foreground="orange")
result_text_widget.tag_configure("success", foreground="green")

#test et butonu oluşturma
tk.Button(root, text="Test Et", width=15, background="green",
          command=lambda: threaded_display_results(function_code_text.get("1.0", tk.END), result_text_widget)).grid(row=5, column=0, padx=10, pady=10)

#grid layout ayarları
root.grid_rowconfigure(3, weight=1)  #fonksiyon girme alanı için ağırlık ayarlama
root.grid_columnconfigure(0, weight=1)  #tüm kolonlar için ağırlık ayarlama

root.mainloop()
