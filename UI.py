import tkinter as tk
import ctypes as ct
import threading
from PIL import Image, ImageTk
import io
import base64
import RAG
import Test_LLM


from tkinter import messagebox

VIEW_BOX = QUERY_BT = CHANGE_LLM = None
root = None
client_socket = None
shift_scroll = 0
grid_widgets = []
model_no = 1

# ----------------------------------------------------------------------------------------------------------------------

def dark_title_bar(window):
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))


def imagen(image_path, screen_width, screen_height, widget):
    def load_image():
        try:
            image = Image.open(image_path)
        except:
            try:
                image = Image.open(io.BytesIO(image_path))
            except:
                binary_data = base64.b64decode(image_path)  # Decode the string
                image = Image.open(io.BytesIO(binary_data))

        image = image.resize((screen_width, screen_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        widget.config(image=photo)
        widget.image = photo  # Keep a reference to the PhotoImage to prevent it from being garbage collected

    image_thread = threading.Thread(target=load_image)  # Create a thread to load the image asynchronously
    image_thread.start()


def ask_binary_choice():
    global CHANGE_LLM, model_no
    if model_no == 2:
        CHANGE_LLM.config(text="Fine_tuned only")
        model_no = 1
    elif model_no == 1:
        CHANGE_LLM.config(text="Fine tuned + RAG")
        model_no = 2
    else:
        pass


def Request_Info(user_query):
    def start(user_query=user_query):
        global VIEW_BOX, QUERY_BT, model_no
        global client_socket

        VIEW_BOX.config(state=tk.NORMAL)
        VIEW_BOX.insert(tk.END, f"\n{user_query}\n", 'user_config')
        VIEW_BOX.see(tk.END)  # Scroll to the end of the text widget
        VIEW_BOX.config(state=tk.DISABLED)

        QUERY_BT.config(text="▫▫▫▫", fg="green", state=tk.DISABLED)
        CHANGE_LLM.config(state=tk.DISABLED)

        if model_no == 1:
                answer = Test_LLM.llm_chain.run(Instruction=user_query)
        else:
                answer = RAG.LLM_Run(str(user_query))

        CHANGE_LLM.config(state=tk.NORMAL)
        VIEW_BOX.config(state=tk.NORMAL)
        VIEW_BOX.insert(tk.END, f"\n{answer}\n", 'llm_config')
        VIEW_BOX.see(tk.END)  # Scroll to the end of the text widget
        VIEW_BOX.config(state=tk.DISABLED)

        QUERY_BT.config(text="►", fg="gray", state=tk.NORMAL)
        CHANGE_LLM.config(state=tk.NORMAL)
    threading.Thread(target=start).start()


def main():
    global VIEW_BOX, QUERY_BT, CHANGE_LLM
    # bg_color = "#1B1B1B"
    # bg_color = "#212122"
    bg_color = "#1F201F"

    app = tk.Tk()

    app.config(bg=bg_color)
    app.maxsize(950, 700)
    app.minsize(950, 700)
    app.title('Lage Language Model')
    # app.attributes("-toolwindow", 1)
    # app.attributes("-topmost", 1)
    # app.overrideredirect(True)
    dark_title_bar(app)

    # Prevent the window from appearing on the taskbar

    on_c = '#2B3230'
    of_c = '#2B2B2C'
    fg_color = 'gray'

    VIEW_BOX_canvas = tk.Frame(app, bg=bg_color, borderwidth=0, border=0)
    VIEW_BOX_canvas.place(relx=0.05, rely=0.1, relheight=0.7, relwidth=0.9)
    # VIEW_DISPLAY, welcome_page_root = attach_scroll(VIEW_BOX)

    VIEW_BOX = tk.Text(VIEW_BOX_canvas, bg=bg_color, borderwidth=0, border=0, font=(13), wrap="word")
    VIEW_BOX.place(relx=0, rely=0, relheight=1, relwidth=1)
    VIEW_BOX.tag_configure("user_config", foreground="#B2BEB5", justify=tk.LEFT)  # user queries  config's
    VIEW_BOX.tag_configure("llm_config", foreground="#54626F", justify=tk.LEFT)  # llm responses config's
    VIEW_BOX.config(state=tk.DISABLED)

    CHANGE_LLM = tk.Button(app, bg=bg_color, fg="#126180", text="Fine_tuned only", activebackground=bg_color, justify=tk.LEFT, anchor="w", font=("Courier New", 12, "italic"), borderwidth=0, border=0,  command=lambda: ask_binary_choice())
    CHANGE_LLM.place(relx=0.05, rely=0.865, relwidth=0.25, relheight=0.04)

    QUERY_ENTRY = tk.Entry(app, bg=of_c, fg="gray", insertbackground='white', justify=tk.CENTER, font=("Courier New", 12, "italic"), borderwidth=0, border=0)
    QUERY_ENTRY.place(relx=0.05, rely=0.92, relwidth=0.9, relheight=0.07)
    QUERY_ENTRY.bind("<Return>", lambda: Request_Info(QUERY_ENTRY.get()))

    QUERY_BT = tk.Button(app, bg=bg_color, activebackground=bg_color, fg="gray", text="►", font=("BOLD", 13), borderwidth=0, border=0, command=lambda: Request_Info(QUERY_ENTRY.get()))
    QUERY_BT.place(relx=0.965, rely=0.92, relheight=0.07, relwidth=0.03)

    app.mainloop()


if __name__ == "__main__":
    main()
