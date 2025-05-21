import platform
import pdfkit
import os


def get_pdfkit_config():
    # Coba path umum untuk berbagai OS
    paths = {
        'Windows': r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
        'Linux': '/usr/bin/wkhtmltopdf',
        'Darwin': '/usr/local/bin/wkhtmltopdf'  # Mac
    }
    
    # Coba path berdasarkan OS
    os_type = platform.system()
    if os_type in paths and os.path.exists(paths[os_type]):
        return pdfkit.configuration(wkhtmltopdf=paths[os_type])
    
    # Jika tidak ditemukan di path standar, coba cari di PATH environment
    try:
        import whichcraft
        wkhtmltopdf_path = whichcraft.which('wkhtmltopdf')
        if wkhtmltopdf_path:
            return pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    except ImportError:
        pass
    
    # Jika semua gagal, return None (akan memunculkan error yang lebih jelas)
    return None