# ULTRA SIMPLE - NO UNICODE, NO ERRORS
import tkinter as tk
import requests
import time

def troll():
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    
    # Try to get image
    img = None
    try:
        import io
        import base64
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        r = requests.get(url, timeout=5)
        img = tk.PhotoImage(data=base64.b64encode(r.content))
        root.image = img
    except:
        pass
    
    # Show images one by one
    count = 0
    
    def show():
        nonlocal count
        if count >= 50:
            return
        
        row = count // 10
        col = 9 - (count % 10)
        x = col * (w // 10)
        y = row * (h // 5)
        
        if img:
            lbl = tk.Label(root, image=img, bg='black')
        else:
            lbl = tk.Label(root, text='X', font=('Arial', 50), fg='white', bg='black')
        
        lbl.place(x=x, y=y)
        count += 1
        
        if count < 50:
            root.after(50, show)
    
    # Start
    root.after(500, show)
    
    # Exit
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.mainloop()

# Run it
troll()
