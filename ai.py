
import os, time, threading, datetime
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog
import psutil, pyttsx3, speech_recognition as sr, cv2
from PIL import Image

# Optional imports
try:
    import google.generativeai as genai
except Exception:
    genai = None
try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

# ------------------------------
# Constants
# ------------------------------
APP_TITLE = "AIVA Assistant"
API_KEY = os.getenv("GOOGLE_API_KEY", "")
WINDOW_SIZE = "1200x800"
EXPORT_DEFAULT = str(Path.home() / "aiva_chat_export.txt")

# ------------------------------
# Init
# ------------------------------
engine = pyttsx3.init()
engine.setProperty("rate", 170)
recognizer = sr.Recognizer()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title(APP_TITLE)
app.geometry(WINDOW_SIZE)
app.minsize(900, 600)
# 🟡 Set custom window + taskbar icon
icon_path = os.path.join(os.path.dirname(__file__), "aiva.ico")
if os.path.exists(icon_path):
    try:
        app.iconbitmap(icon_path)
    except Exception as e:
        print(f"Icon load error: {e}")
# ------------------------------
# Gradient Background
# ------------------------------
bg_canvas = ctk.CTkCanvas(app, highlightthickness=0)
bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

_COLORS = [(26,115,232),(123,31,162),(236,64,122),(255,179,71),(72,219,251)]
_phase = 0.0
_stop_grad = False

def _lerp(c1,c2,t): return tuple(int(a+(b-a)*t) for a,b in zip(c1,c2))
def _hex(c): return "#%02x%02x%02x"%c

def draw_grad():
    global _phase
    w,h = bg_canvas.winfo_width(), bg_canvas.winfo_height()
    i1 = int(_phase)%len(_COLORS)
    i2 = (i1+1)%len(_COLORS)
    t = _phase-int(_phase)
    c1 = _lerp(_COLORS[i1],_COLORS[i2],t)
    c2 = _lerp(_COLORS[(i1+2)%len(_COLORS)],_COLORS[(i1+3)%len(_COLORS)],t)
    bg_canvas.delete("g")
    for i in range(32):
        tt=i/31
        col=_lerp(c1,c2,tt)
        bg_canvas.create_rectangle(int(i*w/32),0,int((i+1)*w/32),h,fill=_hex(col),width=0,tags="g")
    _phase+=0.01
    if _phase>=len(_COLORS): _phase=0
    if not _stop_grad: app.after(30,draw_grad)
app.after(100,draw_grad)

# ------------------------------
# Theme
# ------------------------------
THEME="Gemini"
BUB_USER="#0B84FF"; BUB_AIVA="#1f1f1f"
TEXT_USER="white"; TEXT_AIVA="white"
chat_history=[]

def set_theme(m):
    global THEME,BUB_USER,BUB_AIVA,TEXT_USER,TEXT_AIVA
    THEME=m
    if m=="Light":
        ctk.set_appearance_mode("light")
        BUB_USER="#78b8ff"; BUB_AIVA="#f1f1f1"
        TEXT_USER="black"; TEXT_AIVA="black"
    elif m=="Dark":
        ctk.set_appearance_mode("dark")
        BUB_USER="#0B84FF"; BUB_AIVA="#1f1f1f"
        TEXT_USER="white"; TEXT_AIVA="white"
    else:
        ctk.set_appearance_mode("dark")
        BUB_USER="#0B84FF"; BUB_AIVA="#222"
        TEXT_USER="white"; TEXT_AIVA="white"
    refresh_chat()

# ------------------------------
# Header
# ------------------------------
header=ctk.CTkFrame(app,corner_radius=0)
header.place(relx=0.02,rely=0.02,relwidth=0.96,relheight=0.08)

title=ctk.CTkLabel(header,text=APP_TITLE,font=ctk.CTkFont(size=20,weight="bold"))
title.pack(side="left",padx=15)
sub=ctk.CTkLabel(header,text="Gemini • YOLO • Voice • Webcam",font=ctk.CTkFont(size=11))
sub.pack(side="left",padx=10)

btn_frame=ctk.CTkFrame(header,fg_color="transparent")
btn_frame.pack(side="right",padx=10)

# ------------------------------
# Chat Area (Bubble + Animation)
# ------------------------------
main=ctk.CTkFrame(app,corner_radius=16)
main.place(relx=0.02,rely=0.12,relwidth=0.96,relheight=0.72)

chat=ctk.CTkScrollableFrame(main,corner_radius=12,fg_color="transparent")
chat.grid(row=0,column=0,sticky="nsew",padx=10,pady=10)
main.grid_rowconfigure(0,weight=1)
main.grid_columnconfigure(0,weight=1)

def render_bubble(text,sender):
    bubble_frame=ctk.CTkFrame(chat,fg_color="transparent")
    if sender=="User":
        bubble_frame.pack(fill="x",pady=6,padx=8,anchor="e")
        side="e"; bubble_color=BUB_USER; text_color=TEXT_USER
    else:
        bubble_frame.pack(fill="x",pady=6,padx=8,anchor="w")
        side="w"; bubble_color=BUB_AIVA; text_color=TEXT_AIVA

    bubble=ctk.CTkFrame(bubble_frame,fg_color=bubble_color,corner_radius=20,border_width=0)
    bubble.pack(anchor=side,padx=6)
    lbl=ctk.CTkLabel(bubble,text=text,wraplength=700,justify="left",
                     text_color=text_color,font=ctk.CTkFont(size=13))
    lbl.pack(padx=14,pady=8)

    def animate_in(step=0):
        try:
            if step<5:
                bubble_frame.pack_configure(pady=(10-step*2))
                app.after(20,lambda:animate_in(step+1))
        except: pass
    animate_in()
    chat._parent_canvas.yview_moveto(1.0)

def add_chat(s,t):
    chat_history.append((s,t))
    render_bubble(t,s)

def refresh_chat():
    for w in chat.winfo_children(): w.destroy()
    for s,t in chat_history: render_bubble(t,s)

# ------------------------------
# Typing Animation
# ------------------------------
typing=None; lock=threading.Lock()
def show_typing():
    global typing
    with lock:
        if typing:return
        typing=ctk.CTkLabel(chat,text="AIVA is typing.",text_color="#aaa")
        typing.pack(anchor="w",padx=12,pady=4)
    def loop():
        i=0
        while True:
            with lock:
                if not typing:break
                typing.configure(text="AIVA is typing"+"."*(i%4))
            i+=1; time.sleep(0.5)
    threading.Thread(target=loop,daemon=True).start()
def hide_typing():
    global typing
    with lock:
        if typing: typing.destroy(); typing=None

# ------------------------------
# AI Reply & Voice
# ------------------------------
def speak_async(t): threading.Thread(target=lambda:(engine.say(t),engine.runAndWait()),daemon=True).start()

def get_reply(q):
    if genai and API_KEY:
        try:
            genai.configure(api_key=API_KEY)
            m=genai.GenerativeModel("gemini-2.5-flash")
            r=m.generate_content(q)
            return getattr(r,"text",str(r)).strip()
        except Exception as e: return f"Gemini error: {e}"
    return f"(Offline) You said: {q}"

def reply_thread(q):
    try:
        show_typing(); time.sleep(0.5)
        a=get_reply(q)
    finally:
        hide_typing()
    add_chat("AIVA",a); speak_async(a)

def send_msg(t):
    if not t:return
    add_chat("User",t)
    threading.Thread(target=reply_thread,args=(t,),daemon=True).start()

def listen():
    try:
        with sr.Microphone() as src:
            add_chat("AIVA","🎤 Listening...")
            recognizer.adjust_for_ambient_noise(src,duration=0.6)
            audio=recognizer.listen(src,timeout=6,phrase_time_limit=12)
            try:
                text=recognizer.recognize_google(audio,language="en-IN")
                send_msg(text)
            except sr.UnknownValueError:
                add_chat("AIVA","Sorry, I couldn’t hear clearly.")
            except Exception as e: add_chat("AIVA",f"Mic error: {e}")
    except Exception as e: add_chat("AIVA",f"Microphone error: {e}")

# ------------------------------
# YOLO + Webcam
# ------------------------------
yolo=None
def get_yolo():
    global yolo
    if yolo:return yolo
    try:yolo=YOLO("yolov10x.pt")
    except Exception:yolo=None
    return yolo

def detect_image():
    p=filedialog.askopenfilename(title="Select image",filetypes=[("Images","*.jpg *.png *.jpeg")])
    if not p:return
    m=get_yolo()
    if not m: add_chat("AIVA","⚠ YOLO not found."); return
    add_chat("AIVA","Detecting objects...")
    def run():
        img=cv2.imread(p)
        res=m(img)
        out=res[0].plot()
        cv2.imshow("YOLO - AIVA Detection",out)
        add_chat("AIVA",f"Detected {len(res[0].boxes)} objects. Close window to continue.")
        cv2.waitKey(0); cv2.destroyAllWindows()
    threading.Thread(target=run,daemon=True).start()

def detect_webcam():
    m=get_yolo()
    if not m:
        add_chat("AIVA","⚠ YOLO model not available.")
        return
    add_chat("AIVA","🎥 Starting webcam detection... Press Q to stop.")
    def run():
        cap=cv2.VideoCapture(0)
        if not cap.isOpened():
            add_chat("AIVA","No webcam found.");return
        while True:
            ret,frame=cap.read()
            if not ret:break
            res=m(frame,verbose=False)
            out=res[0].plot()
            cv2.imshow("AIVA Webcam Detection",out)
            if cv2.waitKey(1)&0xFF==ord('q'):break
        cap.release(); cv2.destroyAllWindows()
        add_chat("AIVA","🟢 Webcam detection stopped.")
    threading.Thread(target=run,daemon=True).start()

# ------------------------------
# Gemini Vision
# ------------------------------
def analyze_image():
    if not (genai and API_KEY):
        add_chat("AIVA","⚠ Gemini Vision not configured."); return
    p=filedialog.askopenfilename(title="Select image",filetypes=[("Images","*.jpg *.png *.jpeg")])
    if not p:return
    add_chat("AIVA","🔍 Analyzing image with Gemini Vision...")
    def run():
        try:
            with open(p,"rb") as f: img=f.read()
            m=genai.GenerativeModel("gemini-2.5-flash")
            r=m.generate_content([{"inline_data":{"mime_type":"image/jpeg","data":img}},
                {"text":"Describe this image in detail."}])
            t=getattr(r,"text",str(r))
            add_chat("AIVA",t); speak_async("Image analyzed.")
        except Exception as e: add_chat("AIVA",f"Gemini error: {e}")
    threading.Thread(target=run,daemon=True).start()

# ------------------------------
# Export Chat
# ------------------------------
def export_chat():
    p=filedialog.asksaveasfilename(defaultextension=".txt",initialfile=EXPORT_DEFAULT)
    if not p:return
    with open(p,"w",encoding="utf-8") as f:
        for s,t in chat_history:f.write(f"{s}: {t}\n\n")
    add_chat("AIVA",f"💾 Chat exported to {p}")

# ------------------------------
# Header Buttons
# ------------------------------
ctk.CTkButton(btn_frame,text="🧠 Analyze (Gemini)",width=160,command=analyze_image).pack(side="left",padx=4)
ctk.CTkButton(btn_frame,text="🖼️ Detect (YOLO)",width=140,command=detect_image).pack(side="left",padx=4)
ctk.CTkButton(btn_frame,text="🎥 Webcam",width=120,command=detect_webcam).pack(side="left",padx=4)
ctk.CTkButton(btn_frame,text="💾 Export",width=100,command=export_chat).pack(side="left",padx=4)
theme_var=ctk.StringVar(value="Gemini")
ctk.CTkOptionMenu(btn_frame,values=["Light","Dark","Gemini"],variable=theme_var,command=set_theme).pack(side="left",padx=4)

# ------------------------------
# Input Controls
# ------------------------------
ctrl=ctk.CTkFrame(main,corner_radius=12)
ctrl.grid(row=1,column=0,sticky="ew",padx=10,pady=(0,10))
ctrl.grid_columnconfigure(0,weight=1)

entry=ctk.CTkEntry(ctrl,placeholder_text="Type your message...",height=36)
entry.grid(row=0,column=0,padx=10,pady=10,sticky="ew")

def send_click(): t=entry.get().strip(); entry.delete(0,"end"); send_msg(t)
ctk.CTkButton(ctrl,text="Send",width=90,command=send_click).grid(row=0,column=1,padx=6)
ctk.CTkButton(ctrl,text="🎤",width=56,command=lambda:threading.Thread(target=listen,daemon=True).start()).grid(row=0,column=2,padx=6)
entry.bind("<Return>",lambda e:send_click())

# ------------------------------
# System Info
# ------------------------------
sysf=ctk.CTkFrame(app,corner_radius=12)
sysf.place(relx=0.02,rely=0.86,relwidth=0.96,relheight=0.12)
cpu=ctk.CTkLabel(sysf,text="CPU: --");cpu.place(x=14,y=8)
ram=ctk.CTkLabel(sysf,text="RAM: --");ram.place(x=14,y=36)
disk=ctk.CTkLabel(sysf,text="Disk: --");disk.place(x=200,y=8)
def update_sys():
    try:
        cpu.configure(text=f"CPU: {psutil.cpu_percent():.0f}%")
        ram.configure(text=f"RAM: {psutil.virtual_memory().percent:.0f}%")
        disk.configure(text=f"Disk: {psutil.disk_usage('/').percent:.0f}%")
    except: pass
    app.after(2000,update_sys)
update_sys()

# ------------------------------
# Greeting + Exit
# ------------------------------
add_chat("AIVA","👋 Hello! I'm AIVA — type, speak, or use webcam + YOLO + Gemini Vision.")
def on_close():
    global _stop_grad; _stop_grad=True
    app.destroy()
app.protocol("WM_DELETE_WINDOW",on_close)

# ------------------------------
# Run
# ------------------------------
if __name__=="__main__":
    set_theme("Gemini")
    app.mainloop()


