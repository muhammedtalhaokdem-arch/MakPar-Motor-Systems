import sys
import os
import shutil
import urllib.request
import zipfile

# --- GITHUB AYARLARI ---
GITHUB_USER = "muhammedtalhaokdem-arch" 
GITHUB_REPO = "MakPar-Lang" 
BRANCH = "main"

# Dinamik Yollar
MAKPAR_DIR = os.path.dirname(os.path.abspath(__file__)) 
LIBRARY_DIR = os.path.join(MAKPAR_DIR, "Library")
LIBRARY_DATA_DIR = os.path.join(MAKPAR_DIR, "Library-Data")
PIECE_FILE = os.path.join(LIBRARY_DATA_DIR, "Piece.txt")

ZIP_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"
TEMP_ZIP = os.path.join(MAKPAR_DIR, "temp_libs.zip")
TEMP_EXTRACT = os.path.join(MAKPAR_DIR, "temp_extract")

def control_updates():
    print(f"\n[MLL] Guncellemeler denetleniyor...")
    try:
        req = urllib.request.Request(ZIP_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(TEMP_ZIP, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            
        if os.path.exists(TEMP_EXTRACT):
            shutil.rmtree(TEMP_EXTRACT)
        os.makedirs(TEMP_EXTRACT)
            
        with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
            zip_ref.extractall(TEMP_EXTRACT)
            
        extracted_folder_name = f"{GITHUB_REPO}-{BRANCH}"
        extracted_root_path = os.path.join(TEMP_EXTRACT, extracted_folder_name)
        
        if not os.path.exists(extracted_root_path):
            print("[!] HATA: Depo icerigi okunamadi!")
            return

        remote_files = [f for f in os.listdir(extracted_root_path) if f.endswith('.py') or f == 'plugins.txt']
        remote_count = len(remote_files)
        
        if not os.path.exists(LIBRARY_DATA_DIR):
            os.makedirs(LIBRARY_DATA_DIR)
            
        local_count_str = ""
        if os.path.exists(PIECE_FILE):
            with open(PIECE_FILE, "r", encoding="utf-8") as f:
                local_count_str = f.read().strip()
                
        if not local_count_str:
            with open(PIECE_FILE, "w", encoding="utf-8") as f:
                f.write(str(remote_count))
            print(f"[+] Ilk kayit olusturuldu. Kutuphane sayisi kaydedildi: {remote_count}")
        elif local_count_str == str(remote_count):
            print("There are no updates for the built-in libraries. / Dahili kütüphanelerde bir güncelleme yok.")
        else:
            print("There is an update for the built-in libraries!!!! You can perform the update using the 'mll update' command.")
            print("Dahili kütüphanelerde bir güncelleme var!!!! 'mll update' komutu ile güncellemenizi yapabilirsiniz.")

    except Exception as e:
        print(f"\n[!] KONTROL HATASI: {e}")
    finally:
        if os.path.exists(TEMP_ZIP): os.remove(TEMP_ZIP)
        if os.path.exists(TEMP_EXTRACT): shutil.rmtree(TEMP_EXTRACT)

def update_libraries():
    print(f"\n[MLL] Guncelleme baslatiliyor ve GitHub'dan indiriliyor...")
    try:
        req = urllib.request.Request(ZIP_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(TEMP_ZIP, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            
        if os.path.exists(TEMP_EXTRACT):
            shutil.rmtree(TEMP_EXTRACT)
        os.makedirs(TEMP_EXTRACT)
            
        with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
            zip_ref.extractall(TEMP_EXTRACT)
            
        extracted_folder_name = f"{GITHUB_REPO}-{BRANCH}"
        extracted_root_path = os.path.join(TEMP_EXTRACT, extracted_folder_name)
        
        if not os.path.exists(extracted_root_path):
            print("[!] HATA: Depo icerigi okunamadi!")
            return

        # 1. ESKI KUTUPHANELERI TEMIZLEME: Library klasoru varsa icindekileri tamamen söküp atiyoruz
        if os.path.exists(LIBRARY_DIR):
            shutil.rmtree(LIBRARY_DIR)
        os.makedirs(LIBRARY_DIR) # Temiz bir Library klasörü olustur

        # 2. GitHub'daki güncel dosyaları yeni Library klasörüne kopyala
        remote_files = [f for f in os.listdir(extracted_root_path) if f.endswith('.py') or f == 'plugins.txt']
        
        for file_name in remote_files:
            src_file = os.path.join(extracted_root_path, file_name)
            dst_file = os.path.join(LIBRARY_DIR, file_name)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, dst_file)

        total_remote_count = len(remote_files)
        
        if not os.path.exists(LIBRARY_DATA_DIR):
            os.makedirs(LIBRARY_DATA_DIR)
            
        with open(PIECE_FILE, "w", encoding="utf-8") as f:
            f.write(str(total_remote_count))

        print(f"[BASARILI] Guncelleme tamamlandi! Eski dosyalar temizlendi ve tum kutuphaneler yenilendi.")
        print(f"[BILGI] Guncel kutuphane sayisi Piece.txt dosyasina yazildi: {total_remote_count}")

    except Exception as e:
        print(f"\n[!] GUNCELLEME HATASI: {e}")
    finally:
        if os.path.exists(TEMP_ZIP): os.remove(TEMP_ZIP)
        if os.path.exists(TEMP_EXTRACT): shutil.rmtree(TEMP_EXTRACT)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanim: python mll.py control  VEYA  python mll.py update")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    if command == "control":
        control_updates()
    elif command == "update":
        update_libraries()
    else:
        print(f"[!] Gecersiz MLL komutu: '{command}'")