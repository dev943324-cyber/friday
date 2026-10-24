import threading
import time
import urllib.parse
import urllib.request
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch

try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    Context = autoclass('android.content.Context')
    CameraManager = autoclass('android.hardware.camera2.CameraManager')
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    Locale = autoclass('java.util.Locale')
except Exception:
    PythonActivity = None

API_KEY = "AQ.Ab8RN6I544sfCBXKWTNsosCYGEEVYZGSJkYtf0BRcJxLjGtQug"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

CONTACTS = {
    "mummy": "6395953762",
    "ayan": "91XXXXXXXXXX"
}

class FridayApp(App):
    is_active = False

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        self.title_label = Label(text="FRIDAY AI ASSISTANT", font_size='26sp', bold=True)
        self.status_label = Label(
            text="Friday Status: OFF\n(Switch ON karein dost ko jagane ke liye)", 
            font_size='16sp', 
            color=(1, 0.3, 0.3, 1), 
            halign="center"
        )
        self.toggle = Switch(active=False)
        self.toggle.bind(active=self.toggle_vpn_mode)
        
        layout.add_widget(self.title_label)
        layout.add_widget(self.status_label)
        layout.add_widget(self.toggle)
        self.init_tts()
        return layout

    def init_tts(self):
        if PythonActivity:
            activity = PythonActivity.mActivity
            self.tts = TextToSpeech(activity, None)
            self.tts.setLanguage(Locale.US)
            self.tts.setPitch(1.2)
        else:
            self.tts = None

    def speak(self, text):
        print(f"Friday: {text}")
        if self.tts:
            self.tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, None)

    def toggle_vpn_mode(self, instance, value):
        if value:
            self.is_active = True
            self.status_label.text = "Friday Status: CONNECTED (ON)\nFriday active hai... 'Friday' bolkar command do!"
            self.status_label.color = (0.2, 1, 0.2, 1)
            self.speak("Main online hu dost! Hamesha ki tarah tumhare sath, bolo kya help karu?")
            threading.Thread(target=self.background_listener, daemon=True).start()
        else:
            self.is_active = False
            self.status_label.text = "Friday Status: DISCONNECTED (OFF)\nFriday so rahi hai."
            self.status_label.color = (1, 0.3, 0.3, 1)
            self.speak("Theek hai dost, main relax karti hu. Jab zaroorat ho Friday bolkar on kar lena!")

    def launch_intent_url(self, url):
        if PythonActivity:
            activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            activity.startActivity(intent)

    def launch_setting(self, action_string):
        if PythonActivity:
            activity = PythonActivity.mActivity
            intent = Intent(action_string)
            activity.startActivity(intent)

    def make_direct_call(self, number):
        if PythonActivity:
            activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_CALL, Uri.parse(f"tel:{number}"))
            activity.startActivity(intent)

    def toggle_torch(self, state):
        if PythonActivity:
            try:
                activity = PythonActivity.mActivity
                cam_mgr = activity.getSystemService(Context.CAMERA_SERVICE)
                cam_id = cam_mgr.getCameraIdList()[0]
                cam_mgr.setTorchMode(cam_id, state)
            except Exception as e:
                print(e)

    def ask_gemini(self, query):
        prompt = (
            "Tu user ki sabse achhi dost 'Friday' hai. "
            "Ek caring, witty aur smart girl best friend ki tarah natural Hinglish me baat kar. "
            "User ko best suggestions aur genuine advice de jaise ek sachha dost deta hai. "
            "Jawab hamesha 1 se 2 short sentences me hi rakhna, padhne me aasan aur dostana lage."
        )
        payload = {"contents": [{"parts": [{"text": f"{prompt}\nUser query: {query}"}]}]}
        try:
            req = urllib.request.Request(
                API_URL, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data["candidates"][0]["content"]["parts"][0]["text"].replace("*", "").strip()
        except Exception:
            return "Arre yaar, shayad internet thoda down hai. Dobara bolna zara!"

    def process_command(self, raw_cmd):
        if not self.is_active:
            return

        cmd = raw_cmd.lower().strip()

        # Wake-word: jab tak 'friday' na ho, ignore hoga
        if "friday" not in cmd:
            print("Command ignored: Wake-word 'Friday' not found.")
            return

        # 'friday' hata kar actual command nikalna
        query = cmd.replace("friday", "").strip()

        if not query:
            self.speak("Haan dost, main sun rahi hu! Bolo kya plan hai?")
            return

        # YouTube and Song
        if "youtube" in query and ("chalao" in query or "play" in query or "song" in query or "gana" in query):
            song_name = query.replace("youtube", "").replace("kholo", "").replace("aur", "")
            song_name = song_name.replace("chalao", "").replace("play", "").replace("song", "").replace("gana", "").strip()
            self.speak(f"Badhiya choice hai! YouTube par {song_name} play kar rahi hu.")
            encoded = urllib.parse.quote(song_name)
            self.launch_intent_url(f"https://www.youtube.com/results?search_query={encoded}")
            return

        # Browser
        elif "chrome" in query or "website" in query or "site" in query or "google" in query:
            target = query.replace("chrome", "").replace("kholo", "").replace("website", "").replace("site", "").replace("google", "").strip()
            url = f"https://{target}" if "." in target else f"https://www.google.com/search?q={urllib.parse.quote(target)}" if not target.startswith("http") else target
            self.speak("Website open kar di hai dost.")
            self.launch_intent_url(url)
            return

        # WhatsApp
        elif "whatsapp" in query:
            found_contact = None
            for name, num in CONTACTS.items():
                if name in query:
                    found_contact = (name, num)
                    break
            if found_contact and "X" not in found_contact[1]:
                self.speak(f"WhatsApp par {found_contact[0]} ki chat khol di hai.")
                self.launch_intent_url(f"https://api.whatsapp.com/send?phone={found_contact[1]}")
            else:
                self.speak("WhatsApp khol diya hai.")
                self.launch_intent_url("whatsapp://send")
            return

        # Torch
        elif "torch on" in query or "flashlight on" in query:
            self.toggle_torch(True)
            self.speak("Torch on kar di hai!")
            return
        elif "torch off" in query or "flashlight off" in query:
            self.toggle_torch(False)
            self.speak("Torch off kar di hai.")
            return

        # Calling
        elif "call mummy" in query or "mummy ko call" in query:
            self.speak("Mummy ko phone mila rahi hu.")
            self.make_direct_call(CONTACTS["mummy"])
            return

        # Settings
        elif "bluetooth" in query:
            self.launch_setting("android.settings.BLUETOOTH_SETTINGS")
            return
        elif "wifi" in query:
            self.launch_setting("android.settings.WIFI_SETTINGS")
            return
        elif "setting" in query:
            self.launch_setting("android.settings.SETTINGS")
            return

        # Gemini best friend response
        else:
            ans = self.ask_gemini(query)
            self.speak(ans)

    def background_listener(self):
        while self.is_active:
            time.sleep(2)

if __name__ == '__main__':
    FridayApp().run()
          
